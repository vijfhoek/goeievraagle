<template>
<div id="app">
  <router-view/>
</div>
</template>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-size: 13px;
}

#app {
    font-family: Arial, sans-serif;
    color: #2c3e50;
}

.query__input:hover,
.query__input:focus {
    box-shadow: 0 3px 8px 0 rgba(0,0,0,0.2),0 0 0 1px rgba(0,0,0,0.08);
}

.query__input {
    width: 500px;
    height: 34px;
    line-height: 34px;
    font-size: 16px;
    border: 0;
    border-radius: 2px;
    box-shadow: 0 2px 2px 0 rgba(0,0,0,0.16),0 0 0 1px rgba(0,0,0,0.08);
    transition: box-shadow 200ms cubic-bezier(0.4, 0.0, 0.2, 1);
    padding: 5px 9px 5px 16px;
}
</style>
