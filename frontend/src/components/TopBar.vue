<template>
<div class="topbar">
  <router-link class="logo" to="/">
    <img class="logo__image" src="@/assets/logo.png">
  </router-link>

  <div class="query">
    <input class="query__input" @keyup.enter="search" :value="value">
  </div>
</div>
</template>

<style scoped>
.topbar {
    background-color: rgb(250, 250, 250);
    display: flex;
    flex-flow: row;
    align-items: center;
}

.logo__image {
    width: 180px;
    margin: 20px 16px 12px;
}

.query__input {
    width: 550px;
    margin: 16px;
}
</style>

<script>
import Vue from "vue";
import {Component, Prop} from "vue-property-decorator";

@Component
export default class TopBar extends Vue {
  @Prop() value = "";

  search (event) {
    if (event.target.value.trim().length > 0) {
      this.$emit("input", event.target.value)
    }
  }
}
</script>
