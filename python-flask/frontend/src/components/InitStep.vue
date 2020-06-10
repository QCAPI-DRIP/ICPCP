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

    <form>
    <div class="form-group">
        <label for="workflowUrl">Enter url to workflow file</label>
        <input :class="['input', ($v.form.workflow_url.$error) ? 'is-danger' : '']"
        type="url" class="form-control" id="WorkflowUrl" placeholder="linktoworkflow.cwl" v-model="form.workflow_url">
    </div>
    <div class="form-group">
    <label for="workflowFile">Or specify workflow file</label>
    <b-form-file
      v-model="workflow_file"
      :state="null"
      placeholder="Choose a workflow file"
      drop-placeholder="Drop file here..."
    ></b-form-file>
    </div>
    </form>

</div>
    
    <!-- <upload-btn>
  <template slot="icon">
    <v-icon>add</v-icon>
  </template>
</upload-btn> -->

</template>

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
                form: {
                    workflow_url: '',
                },
                workflow_file: null
            }
        },
        validations: {
            form: {
                workflow_url: {
                    required,
                    url
                }
            }
        },
        watch: {
            form: {
                handler(val){
                    this.$store.commit('set_workflow', val.workflow_url)
                },
                deep: true
            },
             workflow_file: {
                handler(val){
                    if (val != null) {
                        this.$store.commit('set_workflow_file', val)
                        this.$emit('can-continue', {value: true});
                    } else {
                        this.$emit('can-continue', {value: false});
                    }
                }
            },

            $v: {
                handler: function (val) {
                    if(!val.$invalid) {
                        this.$emit('can-continue', {value: true});
                    } else {
                        this.$emit('can-continue', {value: false});
                    }
                },
                deep: true
            },
            clickedNext(val) {
                if(val === true) {
                    this.$v.form.$touch();
                    
                }
            }
        },
        mounted() {
            if(!this.$v.$invalid) {
                this.$emit('can-continue', {value: true});
            } else {
                this.$emit('can-continue', {value: false});
            }
        }
    }

</script>