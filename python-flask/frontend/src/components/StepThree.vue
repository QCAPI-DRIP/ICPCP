<template>
  <div>
      <p> The generated IaaS solution, given the parameters you have selected can be downloaded below. </p>

  </div>
</template>

<script>
export default {
props: ['clickedNext', 'currentStep']
,
watch: {
        $v: {
            handler: function () {
                this.$emit('can-continue', {value: true});

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
            this.$emit('can-continue', {value: true});
        } 
}


</script>

<style>

</style>