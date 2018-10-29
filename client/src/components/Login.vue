<template>
    <div class="container">
        <div class="row">
            <div class="col-md-6 mt-5 mx-auto">
			<alert :message = mymessage v-if="showMessage"></alert>
                <form v-on:submit.prevent="login">
                    <h1 class="h3 mb-3 font-weight-normal">Please sign in</h1>
                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input type="email" v-model="email" class="form-control" name="email" placeholder="Enter email" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" v-model="password" class="form-control" name="password" placeholder="Enter Password" required>
                    </div>
                    <button class="btn btn-lg btn-primary btn-block">Sign in</button>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import router from '../router'
import EventBus from './EventBus'
import Alert from './Alert'

export default {
  data () {
    return {
      email: '',
      password: '',
	  mylogin: '',
	  mymessage: '',
	  showMessage: false,
	  
    }
  },
  
  components: {
	alert: Alert  
  },

  methods: {
    login () {
		var base_url = process.env.ROOT_API;
      axios.post( base_url + '/users/login', {
        email: this.email,
        password: this.password
      }).then((res) => {
	  
		var message = res.data.message;
		var success = res.data.success;	
		console.log('message = ' + message);
		console.log('success = ' + success);
		
		var res_val = res.data['success'];
		if(res_val == "true")
		{
			localStorage.setItem('usertoken', res.data.token);
			var role = res.data.role;
			if(role == "admin")
			{
				this.mylogin = 'admin';
				router.push({ name: 'AdminUsers' })
			}
			else
			{	this.mylogin = 'user';		
				router.push({ name: 'Profile' })
			}
			this.emitMethod()			
		}		
		else
		{
			this.showMessage = true;
			this.mymessage = res.data['message'];	
			this.mylogin = '';
		}		
      }).catch((err) => {
        console.log(err)
      })
	  
		this.email = ''
        this.password = ''		
    },
	
    emitMethod () {
	  EventBus.$emit('logged-in', this.mylogin)
    }
  }
}

</script>
