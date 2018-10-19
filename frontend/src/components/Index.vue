<template>
<div class="index">
  <div class="logo">
    <img class="logo__image" src="@/assets/logo.png">
  </div>
  <div class="query">
    <input class="query__input">
    <div class="query__buttons">
      <input type="button" value="Goeievraagle zoeken" class="query__submit">
      <input type="button" value="Ik doe een gok" class="query__submit">
    </div>
  </div>
</div>
</template>

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
