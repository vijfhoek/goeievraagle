<template>
<div>
  <top-bar v-model="query" />
  <result-body v-model="query" />
</div>
</template>

<script>
import Vue from "vue";
import {Component} from "vue-property-decorator";

import ResultBody from "@/components/ResultBody";
import TopBar from "@/components/TopBar";

@Component({
  "components": {ResultBody, TopBar},
})
export default class Results extends Vue {
  query = "";

  async mounted() {
    this.query = this.$route.query.q;
  }
}
</script>
