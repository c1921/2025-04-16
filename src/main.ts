import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 导入 Waves
import 'node-waves'

// 为 Waves 添加类型声明
declare global {
  interface Window {
    Waves: {
      init: () => void;
      attach: (selector: string, options?: any) => void;
    }
  }
}

// 初始化 Waves
document.addEventListener('DOMContentLoaded', () => {
  if (typeof window.Waves !== 'undefined') {
    window.Waves.init()
    window.Waves.attach('.waves')
  } else {
    console.error('Waves is not defined. Make sure node-waves is correctly loaded.')
  }
})

createApp(App).mount('#app')
