<template>
  <q-page class="row items-center justify-evenly">
    <bar-line-average-speed />
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import BarLineAverageSpeed from 'src/components/BarLineAverageSpeed.vue';

export default defineComponent({
  components: {
    BarLineAverageSpeed,
  },
});
</script>
