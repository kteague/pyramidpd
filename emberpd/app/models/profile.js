import DS from 'ember-data';

var Profile = DS.Model.extend({
  firstName: DS.attr('string'),
  lastLogin:  DS.attr('string')
});

Profile.reopenClass({
  FIXTURES: [
    {
      id: 1,
      firstName: 'Bob Dog',
	  lastLogin: '2014/01/24',
    },
    {
      id: 2,
      firstName: 'Jane Cat',
      lastLogin: '2015/02/23'
    },
  ]
});

export default Profile;