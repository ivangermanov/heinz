<template>
  <q-page class="row items-center justify-evenly">
    <skus-over-time />
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import SkusOverTime from 'src/components/SkusOverTime.vue';

export default defineComponent({
  components: {
    SkusOverTime,
  },
});
</script>
