<script setup lang="ts">
defineProps<{
  class?: string
}>()
</script>

<template>
  <div :class="['animate-shimmer rounded-lg', $props.class]" />
</template>
