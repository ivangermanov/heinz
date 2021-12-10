<template>
  <q-page class="row items-center justify-evenly">
    <skus-heatmap />
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import SkusHeatmap from 'src/components/SkusHeatmap.vue';

export default defineComponent({
  components: {
    SkusHeatmap,
  },
});
</script>
