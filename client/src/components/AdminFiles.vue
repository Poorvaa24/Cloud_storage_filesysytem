<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-18">
        <h1>Files</h1>
        <hr><br><br>
		<alert :message = message v-if="showMessage"></alert>     
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
			  <th scope="col">User</th>
              <th scope="col">Name</th>
              <th scope="col">Last Modified</th>
			  <th scope="col">Created</th>
              <th scope="col">Size</th>
			  <th scope="col">Description</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(file, index) in files" :key="index">
              <td>{{ file.email }}</td>
			  <td>{{ file.filename }}</td>
              <td>{{ file.modified }}</td>
			  <td>{{ file.created }}</td>
              <td>{{ file.size}} bytes</td>
			  <td>{{ file.description}}</td>
              <td>               
                <button type="button" class="btn btn-info btn-sm"  @click="onDownloadFile(file)">Download</button>
				<button type="button" class="btn btn-danger btn-sm"  @click="onDeleteFile(file)">Delete</button>					
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
      files: [],
	  message: '',
	  showMessage: false,
	  myFile:null,	  
    };
  },
  components: {
	alert: Alert  
  },
  methods: {
    getFiles() {
		var base_url = process.env.ROOT_API;
      const path = base_url + '/files';
	  console.log(path);
      axios.get(path)
        .then((res) => {
          this.files = res.data.files;
        })
        .catch((error) => {
          console.error(error);
        });
		this.showMessage = false;
    },
	onDeleteFile(file) {
		var s_email = file.email
		var s_filename = file.filename;		
		console.log(s_email);
		console.log(s_filename);
		this.deleteFile(s_email, s_filename)	
	},
	deleteFile(email, filename) {
		var base_url = process.env.ROOT_API;
	  const path =  base_url + '/files?email='+ email + '&filename=' + filename;
	  console.log(path);
	  axios.delete(path)
		.then((res) => {
		  this.message = 'file deleted!';
		  this.showMessage = true;
		  this.getFiles();
		})
		.catch((error) => {
		  console.error(error);
		  this.getFiles();
		});
	},	
	onDownloadFile(file){
		window.open(file.url);
	},	
  },
  created() {
    this.getFiles();
  },
};
</script>