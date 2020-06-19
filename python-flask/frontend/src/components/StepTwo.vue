<template>
  <div style="padding: 2rem 3rem; text-align: left;">
        <form>

        <b-form-group id="input_input-group-1" label="Enter the raw url to the input below" label-for="input_input-1">
        <b-form-input
          id="input_input-1"
          name="input_input-1"
          v-model="$v.input_url.$model"
          :state="validateState('input_url')"
          aria-describedby="input-1-live-feedback"
          placeholder= "https://pastebin.com/raw/HakSvgsA"
        ></b-form-input>

        <b-form-invalid-feedback
          id="input-1-live-feedback"
        >Please insert a valid url, linking to the input file</b-form-invalid-feedback>
        </b-form-group>
    <!-- <div class="form-group">
        <label for="inputUrl">Enter url to input file</label>
        <input :class="['input', ($v.form.input_url.$error) ? 'is-danger' : '']"
        type="url" class="form-control" id="InputUrl" placeholder="linktoinputfile.yaml" v-model="form.input_url">
    </div> -->

    
    <div class="form-group">
    <label for="inputFile">Or specify input file</label>
    <b-form-file
      v-model="input_file"
      :state="null"
      placeholder="Choose a input file"
      drop-placeholder="Drop file here..."
    ></b-form-file>
    </div>
    </form>
    
    
    
    <!-- <div class="field">
      <label class="label">Enter the url to the performance file below</label>
      <div class="control">
        <input
          :class="['input', ($v.form.performance_url.$error) ? 'is-danger' : '']"
          type="text"
          placeholder="Performance input"
          v-model="form.performance_url"
        >
      </div>
      <p
        v-if="$v.form.performance_url.$error"
        class="help is-danger"
      >
        This url is invalid
      </p>
    </div>
    <div class="field">
      <label class="label">Enter the url to the price file below</label>
      <div class="control">
        <input
          :class="['input', ($v.form.price_url.$error) ? 'is-danger' : '']"
          type="text"
          placeholder="Price input"
          v-model="form.price_url"
        >
      </div>
      <p
        v-if="$v.form.price_url.$error"
        class="help is-danger"
      >
        This url is invalid
      </p>
    </div>
    <div class="field">
      <label class="label">Enter the url to the deadline file below</label>
      <div class="control">
        <input
          :class="['textarea', ($v.form.deadline_url.$error) ? 'is-danger' : '']"
          placeholder="Deadline input"
          v-model="form.deadline_url"
        >
      </div>
      <p
        v-if="$v.form.deadline_url.$error"
        class="help is-danger"
      >
        This url is invalid
      </p>
    </div> -->
  </div>
</template>

<script>
 import {validationMixin} from 'vuelidate'
 import {required, url} from 'vuelidate/lib/validators'

    export default {
        props: ['clickedNext', 'currentStep'],
        mixins: [validationMixin],
        data() {
            return {
                input_url: '',
                input_file: null
            }
        },
         methods: {
        validateState(input_url) {
          const { $dirty, $error } = this.$v[input_url];
          return $dirty ? !$error : null;
        },
        resetForm() {
          this.input_url = '';

          this.$nextTick(() => {
            this.$v.$reset();
          });
        }
         },
        validations: {
                input_url: {
                    required,
                    url
                }
        },
        watch: {
            input_file: {
                handler(val){
                    if (val != null) {
                        this.$store.commit('set_input_file', val)
                        this.$emit('can-continue', {value: true});
                    } else {
                        this.$emit('can-continue', {value: false});
                    }
                }
            },
            $v: {
                handler: function (val) {
                    if(!val.input_url.$invalid) {
                        this.$store.commit('set_input', val.input_url.$model)
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
            if(!this.$v.input_url.$invalid) {
                this.$emit('can-continue', {value: true});
            } else {
                this.$emit('can-continue', {value: false});
            }
        }
    }


</script>