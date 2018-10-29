<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-18">
        <h1>Files</h1>
        <hr><br><br>
		<alert :message = message v-if="showMessage"></alert>
        <button type="button" class="btn btn-success btn-sm" v-b-modal.upload-modal>Add File</button>
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
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
              <td>{{ file.filename }}</td>
              <td>{{ file.modified }}</td>
			  <td>{{ file.created }}</td>
              <td>{{ file.size}} bytes</td>
			  <td>{{ file.description}}</td>
              <td>
                <button type="button" class="btn btn-warning btn-sm" v-b-modal.file-edit-modal @click="onEditFile(file)">Update</button>
                <button type="button" class="btn btn-info btn-sm"  @click="onDownloadFile(file)">Download</button>
				<button type="button" class="btn btn-danger btn-sm"  @click="onDeleteFile(file)">Delete</button>					
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <b-modal ref="uploadFileModal"
             id="upload-modal"
             title="Upload A New File"
             hide-footer>
      <b-form @submit="onUploadSubmit" @reset="onReset" class="w-100">
		
		<b-form-file v-model="uploadFileForm.src" :state="Boolean(file)" ref="fileUpload" placeholder="Choose a file..." required>
		</b-form-file>
		<div class="mt-3">Selected file: {{uploadFileForm.src && uploadFileForm.src.name}}</div>
		<br>
        <b-form-group id="form-description-group"
                      label="Description:"
                      label-for="form-description-input">
            <b-form-input id="form-description-input"
                          type="text"
                          v-model="uploadFileForm.description"
                          required
                          placeholder="Enter Description">
            </b-form-input>
          </b-form-group>
        
        <b-button type="submit" variant="primary">Submit</b-button>
        <b-button type="reset" variant="danger">Reset</b-button>
      </b-form>
    </b-modal>
	
	<b-modal ref="editFileModal"
         id="file-edit-modal"
         title="Edit"
         hide-footer>
  <b-form @submit="onSubmitUpdate" @reset="onResetUpdate" class="w-100">
  <p>Selected file: {{editForm.filename}}</p>
  
    <b-form-group id="form-description-edit-group"
                  label="Description:"
                  label-for="form-description-edit-input">
        <b-form-input id="form-description-edit-input"
                      type="text"
                      v-model="editForm.description"
                      required
                      placeholder="Enter Description">
        </b-form-input>
      </b-form-group>
    <b-button type="submit" variant="primary">Update</b-button>
    <b-button type="reset" variant="danger">Cancel</b-button>
  </b-form>
</b-modal>
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
      uploadFileForm: {
        src: '',
        description: '',
      },
	  message: '',
	  showMessage: false,
	  myFile:null,
	  email: decoded.identity.email,
	  
	  editForm: {
		filename: '',
		description: '',
		size: '',
	  },
    };
  },
  components: {
	alert: Alert  
  },
  methods: {
    getFiles() {
	  var base_url = process.env.ROOT_API;
      const path = base_url + '/files?email=' + this.email;
	  console.log(path);
      axios.get(path)
        .then((res) => {
          this.files = res.data.files;
        })
        .catch((error) => {
          console.error(error);
        });
    },
	onReset(evt) {
      evt.preventDefault();
      this.$refs.uploadFileModal.hide();
      this.initForm();
    },

    initForm() {

		this.editForm.filename = '';
		this.editForm.description = '';
		this.editForm.size = '';
		this.uploadFileForm.src = '';
		this.uploadFileForm.description = '';
		this.$refs.fileUpload.reset();
    },

    onUploadSubmit(evt) {
			  	 	 
      evt.preventDefault();
	  
	  if(this.uploadFileForm.src)
	  {
		  var filename = this.uploadFileForm.src.name;
		  var size  = this.uploadFileForm.src.size;
		  
		  if(size > 10*1024*1024) // 10 MB
		  {
			  alert("File more than 10 MB. Please choose different file")
			  return;
		  }
	  }
	  
      this.$refs.uploadFileModal.hide();
      console.log('File name is ' + this.uploadFileForm.src.name);
	  
	  var data = new FormData();
	  data.append('file', this.uploadFileForm.src);
	  data.append('description', this.uploadFileForm.description);
	  data.append('email', this.email)
      this.uploadFile(data);
      this.initForm();
    },	
    uploadFile(payload) {
		var base_url = process.env.ROOT_API;
      const path = base_url + '/files';
      axios.post(path, payload)
        .then(() => {
          this.getFiles();
		  this.message = 'File Added';
		  this.showMessage = true;
		  
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.getFiles();
        });
    },

	onEditFile(file) {
		this.editForm.filename = file.filename;
		this.editForm.description = file.description;
		this.editForm.size = file.size;
		console.log('File name is '+ file.filename);
		console.log('File Description is ' + file.description);
	},

	onSubmitUpdate(evt) {
		evt.preventDefault();
		this.$refs.editFileModal.hide();
		const payload = {
			filename: this.editForm.filename,
			description: this.editForm.description,
			email: this.email,
			size: this.editForm.size
		};
		this.updateFile(payload);
	},
	
	updateFile(payload) {
		var base_url = process.env.ROOT_API;
	  const path =  base_url + '/files';
	  axios.put(path, payload)
		.then(() => {
		  this.getFiles();
		  this.message = 'File updated!';
		  this.showMessage = true;
		})
		.catch((error) => {
		  console.error(error);
		  this.getFiles();
		});
	},
	
	onResetUpdate(evt) {
	  evt.preventDefault();
	  this.$refs.editFileModal.hide();
	  this.initForm();
	  this.getFiles(); // why?
	},
	onDeleteFile(file) {
		var s_email = this.email
		var s_filename = file.filename;		
		console.log(s_email);
		console.log(s_filename);
		this.deleteFile(s_email, s_filename)	
	},
	deleteFile(email, filename) {
		var base_url = process.env.ROOT_API;
	  const path = base_url + '/files?email='+ email + '&filename=' + filename;
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
		//this.downloadFile(file.name);
		window.open(file.url);
	},	
  },
  created() {
    this.getFiles();
  },
};
</script>