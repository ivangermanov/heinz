import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/Graphs.vue') }],
  },
  {
    path: '/cases-target-vs-actual',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/cases-target-vs-actual',
        component: () => import('pages/CasesTargetActual.vue'),
      },
    ],
  },
  {
    path: '/skus-over-time',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/skus-over-time',
        component: () => import('pages/SkusOverTime.vue'),
      },
    ],
  },
  {
    path: '/predict',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '/predict', component: () => import('pages/Predict.vue') },
    ],
  },
  {
    path: '/skus-heatmap',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/skus-heatmap',
        component: () => import('pages/SkusHeatmap.vue'),
      },
    ],
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/Error404.vue'),
  },
];

export default routes;
