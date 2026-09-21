# Performance Checklist

> Quick reference for performance optimization.

## Core Web Vitals Targets

| Metric                              | Good    | Needs Work | Poor    |
| ----------------------------------- | ------- | ---------- | ------- |
| **LCP** (Largest Contentful Paint)  | < 2.5s  | 2.5-4s     | > 4s    |
| **INP** (Interaction to Next Paint) | < 200ms | 200-500ms  | > 500ms |
| **CLS** (Cumulative Layout Shift)   | < 0.1   | 0.1-0.25   | > 0.25  |

## Frontend Performance

### Critical Render Path

- [ ] Minimize critical CSS (inline above-fold styles)
- [ ] Defer non-critical JavaScript
- [ ] Preload critical resources
- [ ] Optimize font loading (font-display: swap)

### Images

- [ ] Use modern formats (WebP, AVIF)
- [ ] Implement lazy loading
- [ ] Serve responsive sizes (srcset)
- [ ] Use CDN for static assets
- [ ] Set explicit width/height (prevent CLS)

### JavaScript

- [ ] Code splitting (dynamic imports)
- [ ] Tree shaking enabled
- [ ] Bundle size monitored (< 200KB initial)
- [ ] No unused dependencies

### Vue 3 Specific

- [ ] Use `computed` for derived state — not methods called in templates
- [ ] Use `v-memo` for expensive list items that rarely change
- [ ] Use `shallowRef` / `shallowReactive` for large objects that don't need deep reactivity
- [ ] Virtualize long lists (`vue-virtual-scroller`)
- [ ] Avoid `watch` with deep: true on large objects — use specific watchers

```vue
<script setup lang="ts">
import { computed, shallowRef } from "vue";

// ✅ computed — cached, only recalculates when deps change
const sortedItems = computed(() =>
  [...props.items].sort((a, b) => a.name.localeCompare(b.name)),
);

// ✅ shallowRef — large list, only track reference changes
const largeDataset = shallowRef<Row[]>([]);
</script>

<template>
  <!-- ✅ v-memo — skip re-render if selected/focused unchanged -->
  <div v-for="item in items" :key="item.id" v-memo="[item.id === selectedId]">
    <ExpensiveItem :item="item" />
  </div>
</template>
```

## Backend Performance

### Database

- [ ] Indexes on queried columns
- [ ] No N+1 queries
- [ ] Pagination implemented
- [ ] Connection pooling configured
- [ ] Query timeouts set

```python
# ❌ N+1 Problem (Python/SQLAlchemy)
users = (await db.execute(select(UserModel))).scalars().all()
for user in users:
    orders = (await db.execute(
        select(OrderModel).where(OrderModel.user_id == user.id)
    )).scalars().all()

# ✅ Fixed: eager load with selectinload
from sqlalchemy.orm import selectinload
users = (await db.execute(
    select(UserModel).options(selectinload(UserModel.orders))
)).scalars().all()
```

```js
// ❌ N+1 Problem (JS/Prisma)
const users = await db.user.findMany();
for (const user of users) {
  user.orders = await db.order.findMany({ where: { userId: user.id } });
}

// ✅ Fixed: include relation
const users = await db.user.findMany({ include: { orders: true } });
```

### Caching

- [ ] Cache frequently accessed data
- [ ] Appropriate TTLs set
- [ ] Cache invalidation strategy
- [ ] CDN for static content

```python
# Python cache pattern
async def get_user(user_id: str) -> dict:
    cached = await redis.get(f"myapp:v1:user:{user_id}")
    if cached:
        return json.loads(cached)
    user = await user_repo.find_by_id(user_id)
    await redis.setex(f"myapp:v1:user:{user_id}", 3600, json.dumps(user))
    return user
```

### API

- [ ] Response compression (gzip/brotli)
- [ ] Pagination for lists
- [ ] Select only needed fields
- [ ] Async operations for slow tasks (queue them)

```
# ✅ Paginated API
GET /api/v1/users?page=1&limit=20
```

## Measurement Commands

```bash
# Lighthouse (Chrome)
npx lighthouse https://example.com --output=json

# Bundle analysis (Vite)
npm run build -- --report
npx vite-bundle-visualizer

# Database query analysis
EXPLAIN ANALYZE SELECT * FROM users WHERE email = '...';

# Redis latency
redis-cli --latency

# API response time
curl -o /dev/null -s -w '%{time_total}\n' https://api.example.com/users

# Python profiling
python -m cProfile -o profile.stats main.py
python -m pstats profile.stats
```

## Performance Budget

| Resource            | Budget  |
| ------------------- | ------- |
| Initial JS          | < 200KB |
| Initial CSS         | < 50KB  |
| Total page weight   | < 1MB   |
| Time to Interactive | < 3s    |
| API response (p95)  | < 200ms |

## Monitoring

- [ ] Real User Monitoring (RUM) enabled
- [ ] Synthetic monitoring configured
- [ ] Alerting on degradation
- [ ] Performance tracked in CI

```javascript
// Track Core Web Vitals
import { onLCP, onINP, onCLS } from "web-vitals";

onLCP((metric) => sendToAnalytics("LCP", metric.value));
onINP((metric) => sendToAnalytics("INP", metric.value));
onCLS((metric) => sendToAnalytics("CLS", metric.value));
```
