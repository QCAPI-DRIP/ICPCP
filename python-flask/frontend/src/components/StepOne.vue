<template>
  <div style="padding: 2rem 3rem; text-align: left;">
      
    <!-- <div class="field">
      <label class="label">Enter the url to the workflow file below</label>
      <div class="control">
        <input
          :class="['input', ($v.form.workflow_url.$error) ? 'is-danger' : '']"
          type="text"
          placeholder="Specify link to cwl file"
          v-model="form.workflow_url"
        >
      </div>
      <p
        v-if="$v.form.workflow_url.$error"
        class="help is-danger"
      >
        This url is invalid
      </p>
    </div> -->
    <b-form-group id="workflow_input-group-1" label="Enter the raw url to the workflow below" label-for="workflow_input-1">
        <b-form-input
          id="workflow_input-1"
          name="workflow_input-1"
          v-model="$v.workflow_url.$model"
          :state="validateState('workflow_url')"
          aria-describedby="input-1-live-feedback"
          placeholder= "https://raw.githubusercontent.com/x.cwl"
        ></b-form-input>

        <b-form-invalid-feedback
          id="input-1-live-feedback"
        >Please insert a valid url, linking to the workflow file</b-form-invalid-feedback>
      </b-form-group>

    <!-- <form>
    <b-row class="my-1">
    <b-col sm="3">
      <label for="Enter workflow url">Valid State:</label>
    </b-col>
    <b-col sm="9">
      <b-form-input id="input-invalid" 
      :state="$v.workflow_url.$dirty ? !$v.workflow_url.$error : null"
      @input="$v.workflow_url.$touch()" 
      placeholder="Valid input">
      </b-form-input>
    </b-col>
    </b-row> -->

    <!-- <div class="form-group">
        <label for="workflowUrl">Enter url to workflow file</label>
        <input
        type="url" class="form-control" id="WorkflowUrl" placeholder="linktoworkflow.cwl" v-model="workflow_url">
         <p v-if="$v.workflow_url.$error">This url is invalid</p>
    </div> -->


    <div class="form-group">
    <label for="workflowFile">Or specify workflow file</label>
    <b-form-file
      v-model="workflow_file"
      :state="null"
      placeholder="Choose a workflow file"
      drop-placeholder="Drop file here..."
    ></b-form-file>
    </div>
    <!-- </form> -->

</div>
    
    <!-- <upload-btn>
  <template slot="icon">
    <v-icon>add</v-icon>
  </template>
</upload-btn> -->

</template>

<style>
body {
  padding: 1rem;
}
</style>

<script>
 import {validationMixin} from 'vuelidate'
 import {required, url} from 'vuelidate/lib/validators'
 //import UploadFileButton from './UploadFileButton.vue'
//  import UploadButton from 'vuetify-upload-button';

    export default {
        props: ['clickedNext', 'currentStep'],
        mixins: [validationMixin],
        data() {
            return {
                workflow_url: '',
                workflow_file: null
            }
        },
        validations: {
                workflow_url: {
                    url,
                    required
            }
        },
        methods: {
        validateState(workflow_url) {
          const { $dirty, $error } = this.$v[workflow_url];
          return $dirty ? !$error : null;
        },
        resetForm() {
          this.workflow_url = '';

          this.$nextTick(() => {
            this.$v.$reset();
          });
        }
        },
        watch: {
            workflow_url: {
                handler(val){
                    if (val != null) {
                    this.$store.commit('set_workflow', val)
                    this.$emit('can-continue', {value: true});
                 } else {
                        this.$emit('can-continue', {value: false});
                }
                }
            },
             workflow_file: {
                handler(val){
                    if (val !== null) {
                        this.$store.commit('set_workflow_file', val)
                        this.$emit('can-continue', {value: true});
                    } else {
                        this.$emit('can-continue', {value: false});
                    }
                }
            },

            $v: {
                handler: function (val) {
                    if(!val.workflow_url.$invalid) {
                        this.$store.commit('set_workflow', val.workflow_url.$model)
                        this.$emit('can-continue', {value: true});
                    } else {
                        this.$emit('can-continue', {value: false});
                    }
                },
                deep: true
            },
            clickedNext(val) {
                if(val === true) {
                    this.$v.$touch();
                    
                }
            }
        },
        mounted() {
            if(!this.$v.workflow_url.$invalid) {
                this.$emit('can-continue', {value: true});
            } else {
                this.$emit('can-continue', {value: false});
            }
        }
    }
</script>