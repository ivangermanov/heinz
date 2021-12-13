<template>
  <q-page class="row items-center justify-evenly">
    <bar-line-sku-family />
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import BarLineSkuFamily from 'src/components/BarLineSkuFamily.vue';

export default defineComponent({
  components: {
    BarLineSkuFamily,
  },
});
</script>
