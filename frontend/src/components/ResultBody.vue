<template>
<div class="body">
  <div class="suggestions">
    <div v-for="suggestion in json.suggestions" class="suggestion"
         @click="appendToQuery(suggestion.key)">
      {{suggestion.key}}
    </div>
  </div>

  <div class="result-count">
    Ongeveer {{hits}} resultaten ({{responseTime.toFixed(2)}} seconden)
  </div>

  <div class="body__inner">
    <div class="body__facets">
      <div v-for="facet in facets.categories" v-bind:key="facet.category"
            v-bind:class="{active: activeCategories.includes(facet.category)}"
            class="category facet" @click="toggleCategory(facet)">
        <div class="category__facet">{{facet.category}}</div>

        <div v-if="facet.count < 10000" class="category__count">{{facet.count}}</div>
        <div v-else class="category__count">{{(facet.count / 1000).toFixed()}}K</div>
      </div>
    </div>

    <div class="body__results">
      <div v-for="result in results" v-bind:key="result.id" class="result">
        <a :href="result.url" target="_blank">
          <div class="result__title">{{result.title}}</div>
          <div class="result__link">
            {{result.url}} &bullet; {{result.category}} &bullet; {{result.score.toFixed(3)}}
          </div>
          <div class="result__body">
            <span class="result__date">{{result.date}} -</span>
            {{result.body}}
          </div>
        </a>
      </div>
    </div>

    <!--pre>{{JSON.stringify(json, null, 2)}}</pre-->
  </div>
</div>
</template>

<script>
import Vue from "vue";
import {Component, Prop, Watch} from "vue-property-decorator";

@Component
export default class ResultBody extends Vue {
  @Prop() value;

  json = null;
  activeCategories = [];
  hits = 0;
  results = [];
  responseTime = 0;
  facets = {};

  @Watch("value")
  async onQueryChanged(value) {
    await this.search();
  }

  @Watch("$route")
  async onRouteChanged() {
    this.$emit("input", this.$route.query.q);
  }

  async toggleCategory(category) {
    const name = category.category;

    const index = this.activeCategories.indexOf(name);
    if (index === -1) {
      this.activeCategories.push(name);
    } else {
      this.activeCategories.splice(index, 1);
    }

    await this.search();
  }

  async search() {
    const query = encodeURIComponent(this.value);
    let queryString = `?q=${query}`;

    if (this.activeCategories.length > 0) {
      const categories = encodeURIComponent(this.activeCategories.join(","));
      queryString += `&categories=${categories}`;
    }

    this.$router.history.push(`/search${queryString}`);
    const url = `/api/${queryString}`;

    let response = await fetch(url);
    this.json = await response.json();

    this.results = this.json.results;
    this.hits = this.json.hits;
    this.responseTime = this.json.took;
    this.facets = this.json.facets;
  }

  appendToQuery(value) {
    this.$emit("input", `${this.value} AND ${value}`)
  }
}
</script>

<style scoped>
.body {
    width: 100%;
}

.body__inner {
    display: flex;
}

.result-count {
    line-height: 43px;
    color: rgba(0, 0, 0, 0.5);
    margin-left: 208px;
}

.result {
    margin: 24px 0;
    max-width: 600px;
}

.result:first-child {
    margin-top: 12px;
}

.result__title {
    font-size: 18px;
    margin: 1px 0;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.result__link {
    font-size: 14px;
    color: #006621;
}

.result__body {
    margin: 4px 0;

    color: rgba(0, 0, 0, .68);
}

.result__date {
    color: rgba(0, 0, 0, .5);
}

.body__facets {
    width: 184px;
    margin-right: 24px;
}

.facet {
    padding: 4px 8px;
    cursor: pointer;
}

.facet:hover {
    background-color: rgba(0, 0, 0, .1);
}

.facet.active {
    font-weight: bold;
}

.category {
    display: flex;
    justify-content: space-between;
}

.category__facet {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;

    padding-right: 8px;
}

.category__count {
    text-align: right;
}

.suggestions {
    display: flex;
    flex-flow: row wrap;
    max-width: 1000px;
    margin: 12px 0;

    height: 70px;
    overflow-y: hidden;
}

.suggestion {
    border: 1px solid rgba(0, 0, 0, 0.2);
    border-radius: 12px;

    background-color: #f8f8f8;
    padding: 7px 16px;
    margin: 2px;

    cursor: pointer;
}
</style>
