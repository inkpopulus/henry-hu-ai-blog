import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import PostDetail from '../views/PostDetail.vue'
import NewPost from '../views/NewPost.vue'
import Login from '../views/Login.vue'
import ChangePassword from '../views/ChangePassword.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/post/:id', component: PostDetail, props: true },
  { path: '/new', component: NewPost },
  { path: '/edit/:id', component: NewPost, props: true },
  { path: '/login', component: Login },
  { path: '/password', component: ChangePassword },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
