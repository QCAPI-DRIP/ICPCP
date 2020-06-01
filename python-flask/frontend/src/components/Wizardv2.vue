<template>
    <section class="section">
        <div class="container">
            <div class="columns">
                <div class="column is-8 is-offset-2">
                    <horizontal-stepper :steps="demoSteps" @completed-step="completeStep"
                                        @active-step="isStepActive" @stepper-finished="getTosca"
                    >                     
                    </horizontal-stepper>
                </div>
            </div>
        </div>
    </section>
</template>

<script>
import HorizontalStepper from 'vue-stepper';
import axios from 'axios';
import StepOne from './StepOne.vue';
import StepTwo from './StepTwo.vue';
import StepThree from './StepThree.vue';
export default {
    components: {
        HorizontalStepper
    },
    data(){
        return {
            demoSteps: [
                {
                    icon: 'mail',
                    name: 'first',
                    title: 'Workflow file',
                    subtitle: 'Specify workflow',
                    component: StepOne,
                    completed: false

                },
                {
                    icon: 'report_problem',
                    name: 'second',
                    title: 'Sample title 2',
                    subtitle: 'Subtitle sample',
                    component: StepTwo,
                    completed: false
                },

                {
                    icon: 'report_problem',
                    name: 'second',
                    title: 'Sample title 2',
                    subtitle: 'Subtitle sample',
                    component: StepThree,
                    completed: true
                }
            ]
        }
    },
    methods: {
        // Executed when @completed-step event is triggered
         /* eslint no-unused-vars: ["error", { "args": "none" }] */
        completeStep(payload) {
            this.demoSteps.forEach((step) => {
                if (step.name === payload.name) {
                    step.completed = true;
                }
            })
        },
        // Executed when @active-step event is triggered
        isStepActive(payload) {
            this.demoSteps.forEach((step) => {
                if (step.name === payload.name) {
                    if(step.completed === true) {
                        step.completed = false;
                    }
                }
            })
        },
        // Executed when @stepper-finished event is triggered
        getTosca() {
            const path = `http://127.0.0.1:5000/tosca?git_url=https://raw.githubusercontent.com/common-workflow-library/legacy/master/workflows/compile/compile1.cwl&performance_url=https://pastebin.com/raw/yhz2YsFF&deadline_url=https://pastebin.com/raw/1Y7XEFe8&price_url=https://pastebin.com/raw/ZaNbfLzP`;
            axios.get(path)
                .then((res) => {
                    const url = window.URL.createObjectURL(new Blob([res.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', 'IaaS solution.yaml');
                    document.body.appendChild(link);
                    link.click();
                })
                .catch((error) => {
                // eslint-disable-next-line
                console.error(error); 
                });
            },

        alert(payload) {
            alert('end')
        }
    }
}
</script>
