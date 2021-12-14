<template>
  <q-page class="row items-center justify-evenly">
    <current-overfill />
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import CurrentOverfill from 'src/components/CurrentOverfill.vue';

export default defineComponent({
  components: {
    CurrentOverfill,
  },
});
</script>
