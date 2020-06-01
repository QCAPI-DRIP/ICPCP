 <template>

 <div style="padding: 2rem 3rem; text-align: left;">
        <div class="field">
            <label class="label">Enter workflow url</label>
            <div class="control">
                <input :class="['input', ($v.form.workflow.$error) ? 'is-danger' : '']" type="text" placeholder="Specify link to cwl file"
                       v-model="form.workflow">
            </div>
            <p v-if="$v.form.workflow.$error" class="help is-danger">This workflow is invalid</p>
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
                    workflow: '',
                }
            }
        },
        validations: {
            form: {
                workflow: {
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