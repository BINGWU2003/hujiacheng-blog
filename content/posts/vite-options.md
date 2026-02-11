---
title: "Vite 配置选项"
date: 2025-11-27
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 什么是 Vite

[Vite](https://vite.dev/) 是新一代前端构建工具，由 Vue.js 作者尤雨溪开发，提供极速的开发体验和优化的生产构建：

- ⚡ **极速冷启动**：基于原生 ES 模块，无需打包即可启动
- 🔥 **闪电般的 HMR**：热模块替换速度与模块数量无关
- 🛠️ **丰富的功能**：开箱即用支持 TypeScript、JSX、CSS 预处理器等
- 📦 **优化的构建**：预配置的 Rollup 构建，输出高度优化的静态资源
- 🔌 **通用插件**：基于 Rollup 的插件接口，兼容大部分 Rollup 插件
- 🌐 **完全类型化**：灵活的 API 和完整的 TypeScript 类型定义

```bash
# 创建 Vite 项目
npm create vite@latest

# 或使用特定模板
npm create vite@latest my-vue-app -- --template vue
npm create vite@latest my-react-app -- --template react-ts
```

:::tip 版本说明
本文档基于 **Vite 5.x** 编写，同时包含 **Vite 6.x** 的新特性说明。

**Vite 版本历史**：

- ✅ **Vite 6.0**（2024-11-26 发布）：
  - 新增 Environment API（实验性）
  - 支持 Node.js 18、20、22+
  - Sass 默认使用 modern API
  - 改进 CSS 输出文件名自定义
  - npm 下载量：17M+/周

- ✅ **Vite 5.0**（2023 年发布）：
  - 改进开发服务器性能
  - 更好的 CSS 处理
  - npm 下载量：7.5M+/周

**主要特性**：

- ⚡ 开发环境使用原生 ES 模块，无需打包
- 📦 生产环境使用 Rollup 打包，输出优化
- 🔌 兼容 Rollup 插件生态系统
- 🎯 默认支持 TypeScript、JSX、CSS 预处理器
  :::

:::warning 注意事项

- Vite 需要 Node.js 18.0+ 或 20.0+ 版本
- 开发时基于浏览器原生 ES 模块，需要现代浏览器支持
- 某些 CommonJS 依赖可能需要预构建优化
- SSR 应用需要额外配置
  :::

## 配置文件

Vite 使用 `vite.config.js` / `vite.config.ts` 作为配置文件：

```bash
# 配置文件位置（按优先级）
vite.config.js
vite.config.ts
vite.config.mjs
vite.config.cjs
vite.config.mts
vite.config.cts
```

**推荐使用** TypeScript 格式（`vite.config.ts`），本文以 TypeScript 为例。

### 基本配置结构

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  // 项目根目录
  root: process.cwd(),

  // 基础公共路径
  base: "/",

  // 开发服务器配置
  server: {
    port: 3000,
    open: true,
  },

  // 构建配置
  build: {
    outDir: "dist",
    minify: "esbuild",
  },

  // 插件
  plugins: [vue()],
});
```

### 条件配置

根据命令和模式动态配置：

```typescript
import { defineConfig } from "vite";

export default defineConfig(({ command, mode, isSsrBuild, isPreview }) => {
  if (command === "serve") {
    // 开发环境配置
    return {
      server: {
        port: 3000,
      },
      define: {
        __DEV__: true,
      },
    };
  } else {
    // 生产环境配置 (command === 'build')
    return {
      build: {
        minify: "terser",
        sourcemap: true,
      },
      define: {
        __DEV__: false,
      },
    };
  }
});
```

**参数说明**：

| 参数         | 类型                   | 说明                                              |
| ------------ | ---------------------- | ------------------------------------------------- |
| `command`    | `'serve'` \| `'build'` | 开发服务器或生产构建                              |
| `mode`       | `string`               | 当前模式（`development` / `production` / 自定义） |
| `isSsrBuild` | `boolean`              | 是否为 SSR 构建                                   |
| `isPreview`  | `boolean`              | 是否为预览服务器                                  |

### 异步配置

```typescript
import { defineConfig } from "vite";

export default defineConfig(async ({ command, mode }) => {
  const data = await asyncFunction();

  return {
    // 使用异步数据配置
    define: {
      __API_URL__: JSON.stringify(data.apiUrl),
    },
  };
});
```

## 一、核心配置选项

### 1.1 root

**作用**：项目根目录（`index.html` 所在位置）。

```typescript
{
  root: process.cwd(); // 默认值：当前工作目录
}
```

**使用场景**：

```typescript
// 单页应用
{
  root: "./";
}

// 项目在子目录
{
  root: "./src";
}

// Monorepo 项目
{
  root: "./packages/web";
}
```

### 1.2 base

**作用**：开发或生产环境服务的公共基础路径。

```typescript
{
  base: "/"; // 默认值
}
```

**影响对比**：

```typescript
// base: '/'（默认）
// 资源路径：/assets/index.js
<script src="/assets/index.js"></script>

// base: '/my-app/'
// 资源路径：/my-app/assets/index.js
<script src="/my-app/assets/index.js"></script>

// base: './'（相对路径）
// 资源路径：./assets/index.js
<script src="./assets/index.js"></script>
```

**使用场景**：

```typescript
// 部署到子路径（如 GitHub Pages）
{
  base: "/my-repo/";
}

// 部署到 CDN
{
  base: "https://cdn.example.com/";
}

// 相对路径部署
{
  base: "./";
}
```

### 1.3 mode

**作用**：指定应用模式，影响环境变量加载。

```typescript
{
  mode: "development"; // 或 'production'、自定义模式
}
```

**环境变量文件**：

```bash
.env                # 所有模式加载
.env.local          # 所有模式加载，git 忽略
.env.[mode]         # 指定模式加载
.env.[mode].local   # 指定模式加载，git 忽略
```

**优先级**：`mode` 特定文件 > 通用文件，`.local` > 非 `.local`

**示例**：

```bash
# .env.development
VITE_API_URL=http://localhost:3000
VITE_APP_TITLE=My App (Dev)

# .env.production
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=My App
```

```typescript
// 在代码中使用
console.log(import.meta.env.VITE_API_URL);
console.log(import.meta.env.VITE_APP_TITLE);
```

### 1.4 define

**作用**：定义全局常量替换。

```typescript
{
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
    __DEV__: true,
    'process.env.NODE_ENV': JSON.stringify('production')
  }
}
```

**影响对比**：

```typescript
// 配置
{
  define: {
    __API_URL__: JSON.stringify("https://api.example.com");
  }
}

// 源代码
console.log(__API_URL__);

// 编译后
console.log("https://api.example.com");
```

:::warning 注意事项

- 值会被直接插入到代码中，字符串需要 `JSON.stringify()`
- 替换是简单的文本替换，不会解析语法
- 避免定义与全局变量冲突的名称
  :::

### 1.5 plugins

**作用**：配置插件数组。

```typescript
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [vue(), react()],
});
```

**常用插件**：

```typescript
{
  plugins: [
    // Vue
    vue(),
    vueJsx(),

    // React
    react(),

    // 自动导入
    AutoImport({
      imports: ["vue", "vue-router"],
    }),

    // 组件自动注册
    Components({
      resolvers: [ElementPlusResolver()],
    }),

    // 传统浏览器支持
    legacy({
      targets: ["defaults", "not IE 11"],
    }),
  ];
}
```

**条件应用插件**：

```typescript
{
  plugins: [
    vue(),
    // 仅在生产环境使用
    process.env.NODE_ENV === "production" && visualizer(),
    // 仅在构建时使用
    {
      ...legacy(),
      apply: "build",
    },
  ].filter(Boolean);
}
```

### 1.6 resolve.alias

**作用**：定义路径别名。

```typescript
import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@utils": path.resolve(__dirname, "./src/utils"),
      "~": path.resolve(__dirname, "./"),
    },
  },
});
```

**影响对比**：

```typescript
// ❌ 不使用别名
import Button from "../../../components/Button.vue";
import { formatDate } from "../../../utils/date";

// ✅ 使用别名
import Button from "@components/Button.vue";
import { formatDate } from "@utils/date";
```

**TypeScript 配置**：

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}
```

### 1.7 resolve.extensions

**作用**：导入时省略的扩展名列表。

```typescript
{
  resolve: {
    extensions: [".mjs", ".js", ".mts", ".ts", ".jsx", ".tsx", ".json"]; // 默认值
  }
}
```

**影响对比**：

```typescript
// 配置 extensions: ['.js', '.ts', '.vue']

// ✅ 可以省略扩展名
import Button from "./Button"; // 自动解析 Button.vue
import utils from "./utils"; // 自动解析 utils.ts

// ❌ 未配置的扩展名必须显式指定
import data from "./data.json"; // 必须写 .json
```

:::warning 注意事项

- 不建议忽略自定义导入类型（如 `.vue`）的扩展名
- 可能影响 IDE 和类型支持
  :::

### 1.8 publicDir

**作用**：静态资源目录，不会被构建处理，直接复制到输出目录。

```typescript
{
  publicDir: "public"; // 默认值
}
```

**使用场景**：

```
public/
├── favicon.ico
├── robots.txt
└── images/
    └── logo.png
```

**访问方式**：

```html
<!-- 直接使用绝对路径，不需要导入 -->
<img src="/images/logo.png" alt="Logo" />
<link rel="icon" href="/favicon.ico" />
```

**影响对比**：

```typescript
// 普通资源（需要导入）
import logo from './assets/logo.png'
<img src={logo} />

// public 资源（直接引用）
<img src="/logo.png" />
```

:::tip 何时使用 public

- 文件名不需要 hash
- 文件被数千个文件引用
- 文件路径必须固定（如 `robots.txt`）
  :::

## 二、开发服务器配置

### 2.1 server.port

**作用**：开发服务器端口。

```typescript
{
  server: {
    port: 3000,  // 默认：5173
    strictPort: false  // 端口被占用时是否直接退出
  }
}
```

**影响对比**：

```bash
# port: 5173（默认）
VITE v5.4.21  ready in 320 ms
➜  Local:   http://localhost:5173/

# port: 3000
VITE v5.4.21  ready in 320 ms
➜  Local:   http://localhost:3000/

# strictPort: true 且端口被占用
Error: Port 3000 is already in use
```

### 2.2 server.host

**作用**：指定服务器监听的 IP 地址。

```typescript
{
  server: {
    host: "0.0.0.0"; // 监听所有地址
    // host: 'localhost'  // 默认，仅本地访问
    // host: true  // 等同于 '0.0.0.0'
  }
}
```

**使用场景**：

```typescript
// 仅本地开发
{
  server: {
    host: "localhost"; // http://localhost:3000
  }
}

// 局域网访问（移动端调试）
{
  server: {
    host: "0.0.0.0"; // http://192.168.1.100:3000
  }
}
```

### 2.3 server.open

**作用**：启动时自动在浏览器打开。

```typescript
{
  server: {
    open: true,  // 打开默认页面
    // open: '/docs',  // 打开指定路径
    // open: '/docs/index.html'
  }
}
```

### 2.4 server.proxy

**作用**：配置开发服务器代理，解决跨域问题。

```typescript
{
  server: {
    proxy: {
      // 字符串简写
      '/foo': 'http://localhost:4567',

      // 带选项的完整配置
      '/api': {
        target: 'http://jsonplaceholder.typicode.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },

      // 使用正则表达式
      '^/fallback/.*': {
        target: 'http://jsonplaceholder.typicode.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/fallback/, '')
      },

      // WebSocket 代理
      '/socket.io': {
        target: 'ws://localhost:5174',
        ws: true,
        rewriteWsOrigin: true
      }
    }
  }
}
```

**实际应用**：

```typescript
// 开发环境代理配置
{
  server: {
    proxy: {
      '/api': {
        target: 'https://api.example.com',
        changeOrigin: true,
        secure: false,  // 允许 HTTPS 自签名证书
        rewrite: (path) => path.replace(/^\/api/, '/v1')
      }
    }
  }
}

// 前端请求
fetch('/api/users')  // → https://api.example.com/v1/users
```

### 2.5 server.cors

**作用**：配置 CORS。

```typescript
{
  server: {
    cors: true; // 启用默认 CORS
    // 或自定义配置
    // cors: {
    //   origin: 'http://localhost:3001',
    //   credentials: true
    // }
  }
}
```

### 2.6 server.fs

**作用**：限制文件系统访问。

```typescript
import { defineConfig, searchForWorkspaceRoot } from "vite";

export default defineConfig({
  server: {
    fs: {
      // 允许访问的目录
      allow: [
        searchForWorkspaceRoot(process.cwd()),
        "/path/to/custom/directory",
      ],
      // 禁止访问的文件
      deny: [".env", ".env.*", "*.{crt,pem}"],
    },
  },
});
```

### 2.7 server.warmup

**作用**：预热常用文件，提升首次加载速度。

```typescript
{
  server: {
    warmup: {
      clientFiles: [
        './src/components/*.vue',
        './src/utils/big-utils.js'
      ],
      ssrFiles: [
        './src/server/modules/*.js'
      ]
    }
  }
}
```

## 三、构建配置

### 3.1 build.outDir

**作用**：指定输出目录。

```typescript
{
  build: {
    outDir: 'dist',  // 默认值
    emptyOutDir: true  // 构建前清空目录
  }
}
```

### 3.2 build.target

**作用**：设置浏览器兼容性目标。

```typescript
{
  build: {
    target: 'esnext',  // 默认值
    // target: 'es2015',  // 支持旧浏览器
    // target: ['chrome87', 'firefox78', 'safari14']  // 指定浏览器版本
  }
}
```

### 3.3 build.minify

**作用**：代码压缩方式。

```typescript
{
  build: {
    minify: 'esbuild',  // 默认值，使用 esbuild（更快）
    // minify: 'terser',  // 使用 terser（压缩率更高）
    // minify: false,  // 不压缩

    // terser 选项（仅在 minify: 'terser' 时生效）
    terserOptions: {
      compress: {
        drop_console: true,  // 删除 console
        drop_debugger: true  // 删除 debugger
      }
    }
  }
}
```

### 3.4 build.sourcemap

**作用**：生成 source map。

```typescript
{
  build: {
    sourcemap: false,  // 默认值，不生成
    // sourcemap: true,  // 生成独立 .map 文件
    // sourcemap: 'inline',  // 内联到文件中
    // sourcemap: 'hidden'  // 生成但不引用
  }
}
```

### 3.5 build.rollupOptions

**作用**：自定义 Rollup 打包配置。

```typescript
{
  build: {
    rollupOptions: {
      // 外部化依赖（不打包）
      external: ['vue', 'vue-router'],

      // 输出配置
      output: {
        // 分包策略
        manualChunks: {
          'vendor': ['vue', 'vue-router'],
          'utils': ['lodash-es', 'dayjs']
        },

        // 文件命名
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]'
      }
    }
  }
}
```

**高级分包策略**：

```typescript
{
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 将 node_modules 中的包分离
          if (id.includes('node_modules')) {
            return 'vendor'
          }

          // 按目录分包
          if (id.includes('/src/views/')) {
            return 'views'
          }
          if (id.includes('/src/components/')) {
            return 'components'
          }
        }
      }
    }
  }
}
```

### 3.6 build.assetsInlineLimit

**作用**：小于此大小的资源将内联为 base64。

```typescript
{
  build: {
    assetsInlineLimit: 4096; // 默认 4KB
  }
}
```

**影响对比**：

```typescript
// assetsInlineLimit: 4096

// 小文件（<4KB）- 内联
import smallIcon from "./small-icon.png";
// 编译为：data:image/png;base64,iVBORw0KG...

// 大文件（>4KB）- 外部文件
import logo from "./logo.png";
// 编译为：/assets/logo.a3b4c5d6.png
```

## 四、CSS 配置

### 4.1 css.modules

**作用**：配置 CSS Modules。

```typescript
{
  css: {
    modules: {
      // 生成的类名格式
      generateScopedName: '[name]__[local]___[hash:base64:5]',
      // 命名转换
      localsConvention: 'camelCaseOnly',
      // 全局模块路径
      globalModulePaths: [/global\.module\.css$/]
    }
  }
}
```

**使用示例**：

```css
/* Button.module.css */
.button {
  background: blue;
}

.primaryButton {
  background: red;
}
```

```typescript
import styles from "./Button.module.css";

// localsConvention: 'camelCaseOnly'
console.log(styles.button); // "Button__button___a1b2c"
console.log(styles.primaryButton); // "Button__primaryButton___d3e4f"
```

### 4.2 css.preprocessorOptions

**作用**：配置 CSS 预处理器选项。

```typescript
{
  css: {
    preprocessorOptions: {
      // SCSS
      scss: {
        api: 'modern-compiler',  // Vite 5.4+
        additionalData: `@import "@/styles/variables.scss";`,
        // 自动导入变量到每个 scss 文件
        includePaths: ['node_modules']
      },

      // Less
      less: {
        math: 'parens-division',
        globalVars: {
          primary: '#1890ff'
        }
      },

      // Stylus
      styl: {
        define: {
          $specialColor: new stylus.nodes.RGBA(51, 197, 255, 1)
        }
      }
    }
  }
}
```

## 五、依赖优化

### 5.1 optimizeDeps.include

**作用**：强制预构建的依赖。

```typescript
{
  optimizeDeps: {
    include: [
      "vue",
      "vue-router",
      "pinia",
      "axios",
      // 嵌套依赖
      "esm-dep > cjs-dep",
    ];
  }
}
```

**使用场景**：

```typescript
// 动态导入的依赖需要手动包含
{
  optimizeDeps: {
    include: [
      "lodash-es", // 动态导入：() => import('lodash-es')
    ];
  }
}
```

### 5.2 optimizeDeps.exclude

**作用**：排除预构建的依赖。

```typescript
{
  optimizeDeps: {
    exclude: [
      "your-package-name", // 本地开发的包
      "@my-scope/internal-lib",
    ];
  }
}
```

## 六、完整配置示例

### 6.1 Vue 3 + TypeScript 项目

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueJsx from "@vitejs/plugin-vue-jsx";
import path from "path";
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { ElementPlusResolver } from "unplugin-vue-components/resolvers";

export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    AutoImport({
      imports: ["vue", "vue-router", "pinia"],
      resolvers: [ElementPlusResolver()],
      dts: "src/auto-imports.d.ts",
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: "src/components.d.ts",
    }),
  ],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@utils": path.resolve(__dirname, "./src/utils"),
      "@api": path.resolve(__dirname, "./src/api"),
    },
  },

  server: {
    port: 3000,
    open: true,
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: "http://localhost:8080",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },

  build: {
    outDir: "dist",
    sourcemap: false,
    minify: "esbuild",
    rollupOptions: {
      output: {
        manualChunks: {
          "vue-vendor": ["vue", "vue-router", "pinia"],
          "element-plus": ["element-plus"],
          utils: ["axios", "dayjs"],
        },
        chunkFileNames: "js/[name]-[hash].js",
        entryFileNames: "js/[name]-[hash].js",
        assetFileNames: "[ext]/[name]-[hash].[ext]",
      },
    },
  },

  css: {
    preprocessorOptions: {
      scss: {
        api: "modern-compiler",
        additionalData: `@use "@/styles/variables.scss" as *;`,
      },
    },
  },
});
```

### 6.2 React + TypeScript 项目

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [
    react({
      // React Fast Refresh
      fastRefresh: true,
      // Babel 配置
      babel: {
        plugins: [["@babel/plugin-proposal-decorators", { legacy: true }]],
      },
    }),
  ],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@hooks": path.resolve(__dirname, "./src/hooks"),
    },
  },

  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "https://api.example.com",
        changeOrigin: true,
        secure: false,
      },
    },
  },

  build: {
    target: "es2015",
    minify: "terser",
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          "react-vendor": ["react", "react-dom", "react-router-dom"],
          "ui-vendor": ["antd", "@ant-design/icons"],
        },
      },
    },
  },

  esbuild: {
    jsxFactory: "React.createElement",
    jsxFragment: "React.Fragment",
  },
});
```

### 6.3 库模式配置

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, "src/index.ts"),
      name: "MyLib",
      formats: ["es", "cjs", "umd"],
      fileName: (format) => `my-lib.${format}.js`,
    },
    rollupOptions: {
      // 外部化依赖（不打包到库中）
      external: ["vue", "react"],
      output: {
        globals: {
          vue: "Vue",
          react: "React",
        },
      },
    },
  },
});
```

## 七、环境变量

### 7.1 内置环境变量

```typescript
// 在代码中访问
console.log(import.meta.env.MODE); // 'development' 或 'production'
console.log(import.meta.env.BASE_URL); // 基础 URL
console.log(import.meta.env.PROD); // 是否为生产环境
console.log(import.meta.env.DEV); // 是否为开发环境
console.log(import.meta.env.SSR); // 是否为 SSR
```

### 7.2 自定义环境变量

**文件结构**：

```bash
.env                # 所有模式
.env.local          # 所有模式，git 忽略
.env.development    # 开发模式
.env.production     # 生产模式
.env.staging        # 自定义 staging 模式
```

**示例**：

```bash
# .env
VITE_APP_TITLE=My App
VITE_APP_VERSION=1.0.0

# .env.development
VITE_API_URL=http://localhost:3000/api
VITE_DEBUG=true

# .env.production
VITE_API_URL=https://api.example.com
VITE_DEBUG=false
```

**TypeScript 类型定义**：

```typescript
// src/env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string;
  readonly VITE_API_URL: string;
  readonly VITE_DEBUG: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

**在代码中使用**：

```typescript
const apiUrl = import.meta.env.VITE_API_URL;
const isDebug = import.meta.env.VITE_DEBUG === "true";

console.log(`App: ${import.meta.env.VITE_APP_TITLE}`);
```

## 八、常见问题和最佳实践

### 8.1 性能优化

**1. 依赖预构建**：

```typescript
{
  optimizeDeps: {
    include: [
      // 提前包含大型依赖
      "lodash-es",
      "element-plus",
    ];
  }
}
```

**2. 构建优化**：

```typescript
{
  build: {
    // 使用 esbuild 压缩（更快）
    minify: 'esbuild',

    // 分包策略
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // 将大型库分离
            if (id.includes('element-plus')) {
              return 'element-plus'
            }
            if (id.includes('echarts')) {
              return 'echarts'
            }
            return 'vendor'
          }
        }
      }
    },

    // 关闭 sourcemap（生产环境）
    sourcemap: false
  }
}
```

### 8.2 Monorepo 配置

```typescript
import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  resolve: {
    alias: {
      "@my-org/shared": resolve(__dirname, "../shared/src"),
    },
  },

  server: {
    fs: {
      // 允许访问 monorepo 根目录
      allow: ["../.."],
    },
  },

  optimizeDeps: {
    // 排除 workspace 包
    exclude: ["@my-org/shared"],
  },
});
```

### 8.3 生产环境检查清单

```typescript
{
  build: {
    // ✅ 启用代码压缩
    minify: 'esbuild',

    // ✅ 删除 console（可选）
    terserOptions: {
      compress: {
        drop_console: true
      }
    },

    // ✅ 关闭 sourcemap（或使用 'hidden'）
    sourcemap: false,

    // ✅ 合理的分包策略
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router']
        }
      }
    }
  },

  // ✅ 设置正确的 base
  base: '/my-app/',

  define: {
    // ✅ 替换生产环境变量
    __DEV__: false
  }
}
```

### 8.4 常见错误解决

**1. 依赖预构建失败**：

```typescript
{
  optimizeDeps: {
    include: ['problematic-package'],
    // 强制重新预构建
    force: true
  }
}
```

**2. CSS 导入顺序问题**：

```typescript
// 确保全局样式在组件样式之前导入
// main.ts
import "./styles/reset.css"; // 先导入全局样式
import "./styles/global.css";
import App from "./App.vue"; // 后导入组件
```

**3. 路径别名 TypeScript 报错**：

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

## 九、Vite 6.x 新特性

### 9.1 Environment API（实验性）

Vite 6.0 引入了 Environment API，主要面向框架作者，用于支持多环境开发：

```typescript
// vite.config.ts
import { defineConfig } from "vite";

export default defineConfig({
  environments: {
    client: {
      // 浏览器环境配置
    },
    ssr: {
      // SSR 环境配置
    },
    worker: {
      // Web Worker 环境配置
    },
  },
});
```

### 9.2 Node.js 支持更新

- ✅ 支持 Node.js 18、20、22+
- ❌ 移除 Node.js 21 支持

### 9.3 Sass Modern API

```typescript
{
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',  // 默认使用现代 API
        // api: 'legacy'  // 使用旧版 API
      }
    }
  }
}
```

## 十、总结

### 必须配置的选项

1. **plugins** - 框架支持（Vue/React 等）
2. **resolve.alias** - 路径别名
3. **server.port** - 开发服务器端口
4. **server.proxy** - API 代理配置
5. **build.outDir** - 构建输出目录
6. **base** - 部署基础路径

### 推荐工作流

1. 使用官方模板创建项目：`npm create vite@latest`
2. 根据需求添加框架插件（Vue/React）
3. 配置路径别名和环境变量
4. 设置开发服务器和 API 代理
5. 优化构建配置和分包策略
6. 配置 CSS 预处理器（如需要）

### 常用命令

```bash
# 开发服务器
npm run dev
vite

# 生产构建
npm run build
vite build

# 预览生产构建
npm run preview
vite preview

# 使用自定义配置文件
vite --config vite.custom.config.js

# 指定模式
vite --mode staging

# 清除依赖预构建缓存
vite --force
```

## 参考资源

- [Vite 官方文档](https://vite.dev/)
- [Vite 6.0 发布说明](https://vite.dev/blog/announcing-vite6)
- [Vite GitHub 仓库](https://github.com/vitejs/vite)
- [Vite Rollup 插件](https://vite-rollup-plugins.patak.dev/)
- [Awesome Vite](https://github.com/vitejs/awesome-vite)

---

⚡ 使用 Vite，享受极速的开发体验！

## Sources

- [Release Vite 6.0 | Medium](https://medium.com/@onix_react/release-vite-6-0-fe039e69e0ad)
- [Vite 6.0 released | DEVCLASS](https://devclass.com/2024/11/28/vite-6-0-released-but-devs-still-await-rust-powered-future-for-popular-build-tool/)
- [Vite 6.0 is out! | Vite](https://vite.dev/blog/announcing-vite6)
- [Vite Releases](https://vite.dev/releases)
