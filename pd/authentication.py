from zope.interface import implementer
from pyramid.authentication import CallbackAuthenticationPolicy
import time as time_mod
import base64
import hashlib
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.compat import bytes_


def b64encode(v):
    return base64.b64encode(bytes_(v)).strip().replace(b'\n', b'')

def b64decode(v):
    return base64.b64decode(bytes_(v))


class AuthTicket(object):
    """
    This class represents an authentication token.  You must pass in
    the shared secret, the userid and the IP address.
    """

    def __init__(self, secret, userid, ip, hashalg='md5'):
        self.secret = secret
        self.userid = userid
        self.ip = ip
        self.time = time_mod.time()
        self.hashalg = hashalg

    def digest(self):
        return calculate_digest(
            self.ip, self.time, self.secret, self.userid,
            self.hashalg)


class BadTicket(Exception):
    """
    Exception raised when a ticket can't be parsed.  If we get far enough to
    determine what the expected digest should have been, expected is set.
    This should not be shown by default, but can be useful for debugging.
    """
    def __init__(self, msg, expected=None):
        self.expected = expected
        Exception.__init__(self, msg)

def parse_ticket(secret, ticket, ip, hashalg='md5'):
    """
    Parse the ticket, returning (timestamp, userid, tokens).

    If the ticket cannot be parsed, a ``BadTicket`` exception will be raised
    with an explanation.
    """
    ticket = ticket.strip('"')
    digest_size = hashlib.new(hashalg).digest_size * 2
    digest = ticket[:digest_size]
    try:
        timestamp = int(ticket[digest_size:digest_size + 8], 16)
    except ValueError as e:
        raise BadTicket('Timestamp is not a hex integer: %s' % e)
    try:
        userid, data = ticket[digest_size + 8:].split('!', 1)
    except ValueError:
        raise BadTicket('userid is not followed by !')
    userid = url_unquote(userid)

    expected = calculate_digest(ip, timestamp, secret,
                                userid, hashalg)

    # Avoid timing attacks (see
    # http://seb.dbzteam.org/crypto/python-oauth-timing-hmac.pdf)
    if strings_differ(expected, digest):
        raise BadTicket('Digest signature is not correct',
                        expected=(expected, digest))

    tokens = tokens.split(',')

    return (timestamp, userid, tokens)

def calculate_digest(ip, timestamp, secret, userid,
                     hashalg='md5'):
    secret = bytes_(secret, 'utf-8')
    userid = bytes_(userid, 'utf-8')
    hash_obj = hashlib.new(hashalg)

    # Check to see if this is an IPv6 address
    if ':' in ip:
        ip_timestamp = ip + str(int(timestamp))
        ip_timestamp = bytes_(ip_timestamp)
    else:
        # encode_ip_timestamp not required, left in for backwards compatibility
        ip_timestamp = encode_ip_timestamp(ip, timestamp)

    hash_obj.update(ip_timestamp + secret + userid)
    digest = hash_obj.hexdigest()
    hash_obj2 = hashlib.new(hashalg)
    hash_obj2.update(bytes_(digest) + secret)
    return hash_obj2.hexdigest()

def encode_ip_timestamp(ip, timestamp):
    ip_chars = ''.join(map(chr, map(int, ip.split('.'))))
    t = int(timestamp)
    ts = ((t & 0xff000000) >> 24,
          (t & 0xff0000) >> 16,
          (t & 0xff00) >> 8,
          t & 0xff)
    ts_chars = ''.join(map(chr, ts))
    return bytes_(ip_chars + ts_chars)


@implementer(IAuthenticationPolicy)
class EmberAuthTktAuthenticationPolicy(CallbackAuthenticationPolicy):
    """
    An implementaion of AuthTkt that only returns tickets.
    Cookies are handled by Ember.js and ember-simple-auth.
    """

    def __init__(self,
                 secret,
                 callback=None,
                 ):
        self.hashalg = 'sha512'
        self.secret = secret
        self.callback = callback

    def unauthenticated_userid(self, request):
        """Return the identification if the user has a valid token"""
        auth = request.headers.get('Authorization')
        if auth:
            ticket, identification = auth.split(':')
            confirm_ticket = AuthTicket(
                self.secret,
                identification,
                request.remote_addr,
                hashalg=self.hashalg
            )
            if confirm_ticket.digest() == ticket:
                return identification

    def remember(self, request, principal):
        """Returns an AuthTkt ticket
        """
        remote_addr = request.environ['REMOTE_ADDR']
        self.ticket = AuthTicket(
            self.secret,
            principal,
            remote_addr,
            hashalg=self.hashalg
        )
        return self.ticket.digest()

    def forget(self, request):
        return []


