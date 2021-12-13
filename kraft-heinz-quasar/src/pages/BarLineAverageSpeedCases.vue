<template>
  <q-page class="row items-center justify-evenly">
    <bar-line-average-speed-cases />
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import BarLineAverageSpeedCases from 'src/components/BarLineAverageSpeedCases.vue';

export default defineComponent({
  components: {
    BarLineAverageSpeedCases,
  },
});
</script>
