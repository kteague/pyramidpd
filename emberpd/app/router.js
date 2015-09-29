import Ember from 'ember';
import config from './config/environment';

var Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
	this.route('profiles', { path: '/' });
	this.route('about', { path: '/about '});
	this.route('profile', { path: '/profile/:profile_id' });
	
});

export default Router;
