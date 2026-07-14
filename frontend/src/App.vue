<script setup>
import { RouterLink, RouterView } from 'vue-router'

</script>

<template>
  <marquee>Welcome to Placement Portal Application<a href="Student-Placement-Portal-Mad-2-main 2\App_Dev_2_Project_Report_23f3003280_ritik_soni.docx.pdf">Project Report</a> </marquee>
  <header>
    <hr>
    <img alt="Vue logo" class="logo" src="@/assets/image.png" width="425" height="195"  />

    <div class="wrapper">
      <HelloWorld msg="You did it!" />

      <nav>
        <RouterLink to="/">Home</RouterLink>
        
      </nav>
      
    </div>
    
  </header>
  
  <div id ="app-container">
  <RouterView />
  </div>
</template>

<style scoped>

html,
body,
#app,
#app-container {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
}

#app-container {
  background: #eaeef1;
}



header {
  background-color: #81b2b6;
  line-height: 1.5;
  max-height: 50vh;
  text-align: center;
  
}

.logo {
  
  margin: 0 auto 2rem;
  align-self: center;
  fill: #052517;
  border-radius: 35px;

  box-shadow: 0 0 20px rgba(85, 18, 18, 0.25);
  
  
}


nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);

  padding: 10px 20px;
  background-color: #3fa320;
  color: rgb(212, 189, 189);
  text-decoration: none;
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: none;
}

nav a:hover {
  background-color: #05080c;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(116, 134, 83, 0.2);
}
nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  
  header {
    display: block;
    padding-right: 0;
    margin-bottom: 30px;
  }

  .logo {
    margin: 0 auto 2rem;
    align-items: center;
  }

  header .wrapper {
    display: block;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: center;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
