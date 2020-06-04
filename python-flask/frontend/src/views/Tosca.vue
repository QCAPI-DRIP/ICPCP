<template>
  <!-- <div class="container">
      <div>
        <button type="button" class="btn btn-success btn-sm" v-on:click="getTosca()">Download Tosca description</button>
       </div>
  </div> -->

  <div>
    <b-button variant="outline-primary">
      Button
    </b-button>
  </div>
</template>
<script>
import axios from 'axios';
//import Alert from '../components/Alert.vue'

export default {
  data() {
    return {
        variable_1: " "
        }
  },
//   components: {
//     alert: Alert,
//   },
  methods: {
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
    initForm() {
      this.inputFiles.workflow_url = '';
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addWorkflowUrl.hide();
      const payload = this.inputFiles.workflow_url
      this.getTosca(payload);
      this.initForm();
    }
  },
}

</script>