<template>
  <q-page class="row items-center justify-evenly">
    <sku-overfill-heatmap />
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import SkuOverfillHeatmap from 'src/components/SkuOverfillHeatmap.vue';

export default defineComponent({
  components: {
    SkuOverfillHeatmap,
  },
});
</script>
