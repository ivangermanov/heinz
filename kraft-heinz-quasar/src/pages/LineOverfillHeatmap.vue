<template>
  <q-page class="row items-center justify-evenly">
    <line-overfill-heatmap />
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import LineOverfillHeatmap from 'src/components/LineOverfillHeatmap.vue';

export default defineComponent({
  components: {
    LineOverfillHeatmap,
  },
});
</script>
