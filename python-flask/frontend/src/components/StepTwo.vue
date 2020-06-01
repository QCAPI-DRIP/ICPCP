 <template>
 
 <div style="padding: 2rem 3rem; text-align: left;">
        <div class="field">
            <label class="label">performanceURL metrics url</label>
            <div class="control">
                <input :class="['input', ($v.form.performanceURL.$error) ? 'is-danger' : '']" type="text" placeholder="Text input"
                       v-model="form.performanceURL">
            </div>
            <p v-if="$v.form.performanceURL.$error" class="help is-danger">This performanceURL is invalid</p>
        </div>
        <div class="field">
            <label class="label">Price file url</label>
            <div class="control">
                <input :class="['input', ($v.form.priceURL.$error) ? 'is-danger' : '']"  type="text" placeholder="Email input" v-model="form.priceURL">
            </div>
            <p v-if="$v.form.priceURL.$error" class="help is-danger">This email is invalid</p>
        </div>
        <div class="field">
            <label class="label">Deadline file url</label>
            <div class="control">
                <input :class="['textarea', ($v.form.deadlineURL.$error) ? 'is-danger' : '']"  placeholder="Deadline input" v-model="form.deadlineURL">
            </div>
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
                    performanceURL: '',
                    priceURL: '',
                    deadlineURL: ''
                }
            }
        },
        validations: {
            form: {
                performanceURL: {
                    required,
                    url
                },
                priceURL: {
                    required,
                    url
                },
                deadlineURL: {
                    required,
                    url
                }
            }
        },
        watch: {
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