# Vue 3 Patterns

> Mandatory patterns for Vue 3 + TypeScript projects. Always use Composition API with `<script setup>`.

---

## Component Pattern

```vue
<!-- Always <script setup lang="ts"> — never Options API -->
<script setup lang="ts">
import { computed, ref, watch } from "vue";

// ✅ TypeScript generics for props — no runtime overhead
interface Props {
  title: string;
  count?: number;
  variant?: "primary" | "secondary" | "ghost";
}

// ✅ withDefaults for optional props
const props = withDefaults(defineProps<Props>(), {
  count: 0,
  variant: "primary",
});

// ✅ Typed emits
const emit = defineEmits<{
  update: [value: string];
  close: [];
  click: [event: MouseEvent];
}>();

// Local state
const isOpen = ref(false);

// ✅ Computed for derived state — never methods in template
const doubled = computed(() => props.count * 2);

// ✅ Watch with cleanup for async
watch(
  () => props.title,
  async (newTitle, _, onCleanup) => {
    const controller = new AbortController();
    onCleanup(() => controller.abort());
    await fetchData(newTitle, { signal: controller.signal });
  },
);

// ✅ Expose only what parent needs
defineExpose({ focus });
</script>

<template>
  <!-- ✅ One root element or Fragment (<template>) -->
  <div>
    <!-- ✅ key on v-for always -->
    <li v-for="item in items" :key="item.id">{{ item.name }}</li>

    <!-- ✅ v-if over v-show when element is often hidden -->
    <span v-if="isOpen">Content</span>
  </div>
</template>
```

### Component Rules

- Max 200 lines per component — extract sub-components if larger
- No business logic in `components/ui/` — presentation only
- Props down, events up — never mutate props directly
- Always provide `key` on `v-for`

---

## Composable Pattern

```typescript
// composables/useDebounce.ts
import { onUnmounted, ref, watch } from "vue";
import type { Ref } from "vue";

// ✅ Named export, useXxx prefix
export function useDebounce<T>(value: Ref<T>, delay = 300): Ref<T> {
  const debouncedValue = ref<T>(value.value) as Ref<T>;
  let timer: ReturnType<typeof setTimeout>;

  watch(value, (newValue) => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      debouncedValue.value = newValue;
    }, delay);
  });

  // Cleanup on unmount to prevent stale timer firing after component is gone
  onUnmounted(() => clearTimeout(timer));

  return debouncedValue;
}
```

```typescript
// features/users/composables/useUserForm.ts — feature-specific composable
import { ref } from "vue";
import { useForm } from "vee-validate";
import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";

const userSchema = z.object({
  email: z.string().email("Enter a valid email"),
  name: z.string().min(2, "Name must be at least 2 characters"),
});

export function useUserForm() {
  const { handleSubmit, isSubmitting, errors, defineField, resetForm } =
    useForm({
      validationSchema: toTypedSchema(userSchema),
    });

  const [email, emailAttrs] = defineField("email");
  const [name, nameAttrs] = defineField("name");

  return {
    handleSubmit,
    isSubmitting,
    errors,
    resetForm,
    email,
    emailAttrs,
    name,
    nameAttrs,
  };
}
```

### Composable Rules

- Prefix: `useXxx`
- Return reactive refs/computed — not raw values
- Handle cleanup in `onUnmounted` or `watch`'s `onCleanup`
- Global composables → `src/composables/`; feature-specific → `src/features/[name]/composables/`

---

## Pinia Store (Setup Store)

```typescript
// stores/useUserStore.ts
import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { User } from "@/types";

// ✅ Setup Store style (same as composables)
export const useUserStore = defineStore("user", () => {
  // state
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem("token"));

  // getters
  const isAuthenticated = computed(() => !!token.value);
  const fullName = computed(() =>
    user.value ? `${user.value.firstName} ${user.value.lastName}` : "",
  );

  // actions
  function setUser(newUser: User) {
    user.value = newUser;
  }

  function setToken(newToken: string) {
    token.value = newToken;
    localStorage.setItem("token", newToken);
  }

  function logout() {
    user.value = null;
    token.value = null;
    localStorage.removeItem("token");
  }

  return { user, token, isAuthenticated, fullName, setUser, setToken, logout };
});
```

### Pinia Rules

- Use Setup Store style (not Options Store)
- Store name: `useXxxStore`
- Global state only — local state stays in component/composable
- Never access store outside `<script setup>` or composables (no top-level access)

---

## Data Fetching (TanStack Query)

```typescript
// features/users/composables/useUser.ts
import { computed } from "vue";
import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import type { Ref } from "vue";
import { usersApi } from "@/api/endpoints/users.api";

// ✅ Wrap useQuery in composable
export function useUser(userId: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ["user", userId.value]),
    queryFn: () => usersApi.getById(userId.value),
    staleTime: 60_000,
    enabled: computed(() => !!userId.value),
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: usersApi.update,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["user", variables.id] });
    },
  });
}
```

```vue
<!-- Usage: always handle all 3 states -->
<script setup lang="ts">
const { data: user, isPending, isError, refetch } = useUser(userId);
</script>

<template>
  <SkeletonLoader v-if="isPending" />
  <ErrorMessage v-else-if="isError" @retry="refetch" />
  <UserProfile v-else :user="user" />
</template>
```

### TanStack Query Rules

- Always handle `isPending`, `isError`, and success states
- Query keys: `['resource', id]` — consistent shape across app
- `staleTime` default: 60s for most data; 0 for frequently updated
- Use `invalidateQueries` after mutations, not manual cache updates

---

## Axios API Client

```typescript
// api/index.ts
import axios from "axios";
import { useUserStore } from "@/stores/useUserStore";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10_000,
});

// ✅ Attach token on every request
// useUserStore() called INSIDE the callback — not at module level.
// Calling it at module level fails because Pinia is not installed yet at import time.
apiClient.interceptors.request.use((config) => {
  const userStore = useUserStore();
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`;
  }
  return config;
});

// ✅ Handle 401 globally
// Trade-off: response.data unwrap means consumers get data directly but lose
// access to response.headers and response.status in the success path.
// If you need headers, remove this interceptor and unwrap manually in each api function.
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      useUserStore().logout();
    }
    return Promise.reject(error);
  },
);
```

```typescript
// api/endpoints/users.api.ts
import { apiClient } from "@/api";
import type { User } from "@/types";

export const usersApi = {
  getById: (id: string): Promise<User> => apiClient.get(`/api/v1/users/${id}`),
  update: (data: { id: string } & Partial<User>): Promise<User> =>
    apiClient.patch(`/api/v1/users/${data.id}`, data),
};
```

---

## Form Pattern (VeeValidate + Zod)

```vue
<!-- features/auth/components/LoginForm.vue -->
<script setup lang="ts">
import { useForm } from "vee-validate";
import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";
import { useAuthStore } from "../stores/auth.store";

const schema = toTypedSchema(
  z.object({
    email: z.string().email("Enter a valid email"),
    password: z.string().min(8, "Password must be at least 8 characters"),
  }),
);

const { handleSubmit, isSubmitting, errors, defineField } = useForm({
  validationSchema: schema,
});

const [email, emailAttrs] = defineField("email");
const [password, passwordAttrs] = defineField("password");

// ✅ Store accessed at top of setup — not inline inside callbacks
const authStore = useAuthStore();
const onSubmit = handleSubmit(async (values) => {
  await authStore.login(values);
});
</script>

<template>
  <form novalidate @submit="onSubmit">
    <div>
      <label for="email">Email</label>
      <input
        id="email"
        v-model="email"
        type="email"
        v-bind="emailAttrs"
        :aria-invalid="!!errors.email"
      />
      <p v-if="errors.email" role="alert">{{ errors.email }}</p>
    </div>

    <div>
      <label for="password">Password</label>
      <input
        id="password"
        v-model="password"
        type="password"
        v-bind="passwordAttrs"
        :aria-invalid="!!errors.password"
      />
      <p v-if="errors.password" role="alert">{{ errors.password }}</p>
    </div>

    <BaseButton type="submit" :loading="isSubmitting">
      {{ isSubmitting ? "Signing in..." : "Sign in" }}
    </BaseButton>
  </form>
</template>
```

---

## Vue Router + Auth Guard

```typescript
// router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import { authGuard } from "./guards/auth.guard";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: () => import("@/views/HomeView.vue"), // ✅ Lazy load all views
    },
    {
      path: "/login",
      component: () => import("@/views/auth/LoginView.vue"),
      meta: { guestOnly: true },
    },
    {
      path: "/dashboard",
      component: () => import("@/views/dashboard/DashboardView.vue"),
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach(authGuard);
export default router;
```

```typescript
// router/guards/auth.guard.ts
import type { NavigationGuardNext, RouteLocationNormalized } from "vue-router";
import { useUserStore } from "@/stores/useUserStore";

export function authGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext,
): void {
  // useUserStore() is safe here only because router.beforeEach runs after
  // app.use(pinia) — ensure pinia is installed before createRouter() in main.ts
  const { isAuthenticated } = useUserStore();

  if (to.meta.requiresAuth && !isAuthenticated) return next("/login");
  if (to.meta.guestOnly && isAuthenticated) return next("/dashboard");
  next();
}
```

---

## TypeScript Rules

```typescript
// ✅ Strict types everywhere — tsconfig strict: true
// ✅ Use type imports for type-only imports
import type { User } from "@/types";

// ✅ Narrow union types properly
function processUser(user: User | null): string {
  if (!user) return "Guest";
  return user.name;
}

// ❌ Never use any without a comment explaining why
const data: any = response; // ❌

// ✅ Use unknown + type guard instead
function isUser(val: unknown): val is User {
  return typeof val === "object" && val !== null && "id" in val;
}
```
