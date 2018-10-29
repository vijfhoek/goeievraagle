<template>
<div class="body">
  <div class="chips">
    <div v-for="chip in chips" v-bind:key="chip.key" class="chip" @click="appendToQuery(chip.key)">
      {{chip.key}}
    </div>
  </div>

  <div class="result-count">
    Ongeveer {{hits}} resultaten ({{responseTime.toFixed(2)}} seconden)
  </div>

  <div class="body__inner">
    <div class="body__facets">
      <div class="body__categories">
        <div v-for="facet in facets.categories" v-bind:key="facet.category"
             v-bind:class="{active: activeCategories.includes(facet.category)}"
             class="category facet" @click="toggleCategory(facet)">
          <div class="category__facet">{{facet.category}}</div>

          <div v-if="facet.count < 10000" class="category__count">{{facet.count}}</div>
          <div v-else class="category__count">{{(facet.count / 1000).toFixed()}}K</div>
        </div>
      </div>

      <div class="body__dates">
        <div v-for="{count, key} in facets.dates" v-bind:key="key"
             v-bind:class="{active: activeYears.includes(key)}"
             class="facet date" @click="toggleYear(key)">
          <div class="date__facet">{{key}}</div>

          <div v-if="count < 10000" class="date__count">{{count}}</div>
          <div v-else class="date__count">{{(count / 1000).toFixed()}}K</div>
        </div>
      </div>
    </div>

    <div class="body__results">
      <div v-for="result in results" v-bind:key="result.id" class="result">
        <a :href="result.url" target="_blank">
          <div class="result__title">
            {{result.title}}
            <span v-if="result.dead">(404)</span>
          </div>
          <div class="result__link">
            {{result.url}} &bullet; {{result.category}} &bullet; {{result.score.toFixed(3)}}
          </div>
          <div class="result__body">
            <span class="result__date">{{result.date}} -</span>
            {{result.body}}
          </div>
        </a>
      </div>

      <div class="pagination">
        <div class="pagination__page">
          <img src="@/assets/pages_start.png" />
        </div>

        <div v-for="page in pages" class="pagination__page"
             v-if="page > currentPage - 5 && page < currentPage + 5"
             v-bind:class="{active: page === currentPage}" @click="switchPage(page)"
             v-bind:key="page">
          <img v-if="page === currentPage" src="@/assets/pages_active.png" />
          <img v-else src="@/assets/pages_inactive.png" />

          {{page}}
        </div>

        <div class="pagination__page">
          <img src="@/assets/pages_end.png" />
        </div>
      </div>
    </div>
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
  hits = 0;
  results = [];
  responseTime = 0;
  facets = {dates: [], categories: []};
  chips = [];
  dates = {}

  activeCategories = [];
  activeYears = [];

  currentPage = 1;

  get pages() {
    return Math.ceil(this.hits / 10);
  }

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

  async toggleYear(year) {
    const index = this.activeYears.indexOf(year);
    if (index === -1) {
      this.activeYears.push(year);
    } else {
      this.activeYears.splice(index, 1);
    }

    await this.search();
  }

  async search() {
    const query = encodeURIComponent(this.value);
    let queryString = `?q=${query}&page=${this.currentPage}`;

    if (this.activeCategories.length > 0) {
      const categories = encodeURIComponent(this.activeCategories.join(","));
      queryString += `&categories=${categories}`;
    }
    if (this.activeYears.length > 0) {
      const years = encodeURIComponent(this.activeYears.join(","));
      queryString += `&years=${years}`;
    }

    this.$router.history.push(`/search${queryString}`);
    const url = `/api/${queryString}`;

    let response = await fetch(url);
    this.json = await response.json();

    this.chips = this.json.chips;
    this.facets = this.json.facets;
    this.hits = this.json.hits;
    this.responseTime = this.json.took;
    this.results = this.json.results;

    console.log({...this.facets});
  }

  appendToQuery(value) {
    this.$emit("input", `${this.value} +${value}`);
  }

  async switchPage(page) {
    this.currentPage = page;
    await this.search();
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

.category,
.date {
    display: flex;
    justify-content: space-between;
}

.category__facet,
.date__facet {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;

    padding-right: 8px;
}

.category__count,
.date__count {
    text-align: right;
}

.chips {
    display: flex;
    flex-flow: row wrap;
    max-width: 1000px;
    margin: 12px 0;

    height: 70px;
    overflow-y: hidden;
}

.chip {
    border: 1px solid rgba(0, 0, 0, 0.2);
    border-radius: 12px;

    background-color: #f8f8f8;
    padding: 7px 16px;
    margin: 2px;

    cursor: pointer;
    height: 32px;
}

.pagination {
    display: flex;
    margin: 0 0 16px;
}

.pagination__page {
    height: 50px;
    text-align: center;
    display: flex;
    flex-flow: column;
}

.pagination img {
    height: 40px;
    margin: 0 1px;
}

.pagination__page:not(.active) {
    text-decoration: underline;
    color: blue;
    cursor: pointer;
}

.body__categories,
.body__dates {
    margin-bottom: 16px;
}
</style>
