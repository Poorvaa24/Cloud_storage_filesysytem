<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Users</h1>
        <hr><br><br>
		<alert :message = message v-if="showMessage"></alert>
		<br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">First Name</th>
              <th scope="col">Last Name</th>
			  <th scope="col">Email</th>
              <th scope="col">Created</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in users" :key="index">
              <td>{{ user.first_name }}</td>
              <td>{{ user.last_name }}</td>
			  <td>{{ user.email }}</td>
              <td>{{ user.created}}</td>            
			  <td>
			  <button type="button" class="btn btn-danger btn-sm"  @click="onDeleteUser(user)">Delete</button>
			  </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>    	
  </div>
</template>

<script>
import axios from 'axios';
import Alert from './Alert'
import jwtDecode from 'jwt-decode'

export default {
  data() {
	
	const token = localStorage.usertoken
    const decoded = jwtDecode(token)

    return {
      users: [],
	  message: '',
	  showMessage: false,
    };
  },
  components: {
	alert: Alert  
  },
  methods: {
    getUsers() {
		var base_url = process.env.ROOT_API;
      const path = base_url + '/users';
	  console.log(path);
      axios.get(path)
        .then((res) => {
          this.users = res.data.users;
		  console.log(this.users);
        })
        .catch((error) => {
          console.error(error);
        });
    },
	
	onDeleteUser(user) {
		var s_email = user.email;		
		console.log(s_email);
		this.deleteUser(s_email)	
	},
	
	deleteUser(email) {
		var base_url = process.env.ROOT_API;
	  const path = base_url + `/users/${email}`;
	  console.log(path);
	  axios.delete(path)
		.then((res) => {
		  this.message = 'User and Its Files deleted!';
		  this.showMessage = true;
		  this.getUsers();
		})
		.catch((error) => {
		  console.error(error);
		  this.getUsers();
		});
	},	

	
  },
  created() {
    this.getUsers();
  },
};
</script>