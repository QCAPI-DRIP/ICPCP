<template>
  <div style="padding: 2rem 3rem; text-align: left;">
    <div class="field">
      <label class="label">Enter the url to the performance file below</label>
      <div class="control">
        <input
          :class="['input', ($v.form.performance_url.$error) ? 'is-danger' : '']"
          type="text"
          placeholder="Text input"
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
          placeholder="Email input"
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
    </div>
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
                form: {
                    performance_url: '',
                    price_url: '',
                    deadline_url: ''
                }
            }
        },
        validations: {
            form: {
                performance_url: {
                    required,
                    url
                },
                price_url: {
                    required,
                    url
                },
                deadline_url: {
                    required,
                    url
                }
            }
        },
        computed: {
            performance() {
                return this.form.performance_url;
            },
            price() {
                return this.form.price_url;
            },
            deadline() {
                return this.form.deadline_url;
            }
        },
        watch: {
            performance() {
                    this.$store.commit('set_performance', this.form.performance_url)
                },
            price() {
                    this.$store.commit('set_price', this.form.price_url)
            },
            deadline() {
                    this.$store.commit('set_deadline', this.form.deadline_url)
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