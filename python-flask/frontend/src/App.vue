<template>
  <div id="app">
    <div id="nav">
      <router-link to="/">Home</router-link>
      <!-- <router-link to="/about">About</router-link> | -->
      <!-- <router-link to="/courses">Courses</router-link> |
      <router-link to="/ping">Ping</router-link> |
      <router-link to="/tosca">Tosca</router-link> |
      <router-link to="/wizard">Wizard</router-link> |
      <router-link to="/wizardv2">Wizardv2</router-link>  -->
    </div>
    <router-view/>
  </div>
</template>

<style>
#app {
  margin-top: 60px
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}

label.label {
          color: #333333;
          font-weight: bold;
          font-size: large;
}
/* p.form-data

          .step-subtitle {
            font-weight: lighter;
            margin: 0;
            color: #555555;
          }
        } */
</style>
