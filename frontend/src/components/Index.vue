<template>
<div class="index">
  <div class="logo">
    <img class="logo__image" src="@/assets/logo.png">
  </div>
  <div class="query">
    <input class="query__input" v-model="query" @keyup.enter="search">
    <div class="query__buttons">
      <input type="button" value="Goeievraagle zoeken" class="query__submit" @click="search">
      <input type="button" value="Ik doe een gok" class="query__submit" @click="lucky">
    </div>
  </div>
</div>
</template>

<script>
import Vue from "vue";
import {Component} from "vue-property-decorator";

@Component
export default class Index extends Vue {
  query = "";

  search() {
    const query = encodeURIComponent(this.query);
    this.$router.push(`/search?q=${query}`);
  }

  lucky() {
  }
}
</script>

<style scoped>
.index {
    text-align: center;
}

.logo {
    margin-top: 230px;
    margin-bottom: 30px;
}

.logo__image {
    width: 472px;
}

.query__input {
    margin-bottom: 20px;
}

.query__buttons > input {
    background-color: #f2f2f2;
    border: 1px solid #f2f2f2;
    border-radius: 2px;
    color: rgba(0, 0, 0, .75);

    font-size: 13px;
    font-weight: bold;
    line-height: 27px;

    margin: 11px 4px;

    height: 36px;
    min-width: 54px;
    padding: 0 16px;
}
</style>
