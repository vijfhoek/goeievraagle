<template>
<div>
  <div class="topbar">
    <div class="logo">
      <img class="logo__image" src="@/assets/logo.png">
    </div>

    <div class="query">
      <input class="query__input" v-model="query" @change="getResults">
    </div>
  </div>

  <div class="body">
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
            <div class="result__link">{{result.url}}</div>
            <div class="result__body">
              <span class="result__date">{{result.date}} -</span>
              {{result.body}}
            </div>
          </a>
        </div>
    </div>
    </div>
  </div>
</div>
</template>

<style scoped>
a {
    text-decoration: none;
}

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
</style>

<script>
import Vue from "vue";
import {Component} from "vue-property-decorator";

@Component
export default class Results extends Vue {
  query = "";
  
  hits = 0;
  results = [];
  facets = {};
  
  activeCategories = [];
  
  responseTime = 0.0;
  
  async toggleCategory(category) {
    const name = category.category;
    
    const index = this.activeCategories.indexOf(name);
    if (index === -1) {
      this.activeCategories.push(name);
    } else {
      this.activeCategories.splice(index, 1);
    }
    
    await this.getResults();
  }
  
  async getResults() {
    let url = `/api/?q=${this.query}`;
    
    if (this.activeCategories.length > 0) {
      const categories = encodeURIComponent(this.activeCategories.join(","));
      url += `&categories=${categories}`;
    }
    
    let response = await fetch(url);
    let json = await response.json();

    this.results = json.results;
    this.hits = json.hits;
    this.responseTime = json.took;
    this.facets = json.facets;
  }

  async mounted() {
    await this.getResults();
  }
}
</script>
