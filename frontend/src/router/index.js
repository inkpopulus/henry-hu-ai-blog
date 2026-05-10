import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '../stores/auth'
import Home from '../views/Home.vue'
import PostDetail from '../views/PostDetail.vue'
import NewPost from '../views/NewPost.vue'
import Login from '../views/Login.vue'
import ChangePassword from '../views/ChangePassword.vue'
import NotFound from '../views/NotFound.vue'
import Lab from '../views/Lab.vue'
import LabA from '../views/LabA.vue'
import LabB from '../views/LabB.vue'
import LabC from '../views/LabC.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/post/:id', component: PostDetail, props: true },
  { path: '/new', component: NewPost, meta: { requiresAuth: true } },
  { path: '/edit/:id', component: NewPost, props: true, meta: { requiresAuth: true } },
  { path: '/login', component: Login },
  { path: '/password', component: ChangePassword, meta: { requiresAuth: true } },
  {
    path: '/lab',
    component: Lab,
    meta: { requiresAuth: true },
    children: [
      { path: 'a', component: LabA },
      { path: 'b', component: LabB },
      { path: 'c', component: LabC },
    ],
  },
  { path: '/:pathMatch(.*)*', component: NotFound },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  if (auth.loading) {
    await auth.check()
  }
  if (to.meta.requiresAuth && !auth.loggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

export default router
