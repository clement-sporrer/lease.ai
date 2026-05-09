# Design tokens

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Colors

```ts
export const colors = {
  navy: {
    900: '#0D183D',
    800: '#142452',
    700: '#1A3168',
  },
  blue: {
    50: '#E9F2FF',
    100: '#D8E8FF',
    500: '#2563EB',
    600: '#1D4ED8',
    700: '#1E40AF',
  },
  teal: {
    50: '#E7F8F3',
    500: '#10B981',
    600: '#059669',
  },
  gray: {
    50: '#F7F9FB',
    100: '#F1F5F9',
    200: '#E5E7EB',
    300: '#CBD5E1',
    500: '#64748B',
    700: '#334155',
  },
  white: '#FFFFFF',
  danger: '#EF4444',
  warning: '#F59E0B',
};
```

## Spacing

```ts
export const spacing = {
  0: 0,
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  8: 32,
  10: 40,
  12: 48,
};
```

## Radius

```ts
export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  pill: 999,
};
```

## Typography

```ts
export const typography = {
  h1: { fontFamily: 'Satoshi-Bold', fontSize: 34, lineHeight: 40, letterSpacing: -0.8 },
  h2: { fontFamily: 'Satoshi-Bold', fontSize: 26, lineHeight: 32, letterSpacing: -0.5 },
  title: { fontFamily: 'Satoshi-Bold', fontSize: 20, lineHeight: 26 },
  body: { fontFamily: 'Satoshi-Regular', fontSize: 16, lineHeight: 24 },
  small: { fontFamily: 'Satoshi-Regular', fontSize: 13, lineHeight: 18 },
  label: { fontFamily: 'Satoshi-Medium', fontSize: 12, lineHeight: 16, letterSpacing: 0.4 },
  dataLg: { fontFamily: 'IBMPlexMono-Medium', fontSize: 28, lineHeight: 34 },
  dataMd: { fontFamily: 'IBMPlexMono-Medium', fontSize: 18, lineHeight: 24 },
};
```

## Shadows

```ts
export const shadows = {
  card: {
    shadowColor: '#0D183D',
    shadowOpacity: 0.06,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 8 },
    elevation: 3,
  },
};
```

## Status colors

```ts
export const statusColors = {
  draft: colors.gray[500],
  submitted: colors.blue[500],
  missing_documents: colors.warning,
  pre_approved: colors.teal[500],
  refi_review: colors.blue[600],
  financier_approved: colors.teal[600],
  rejected: colors.danger,
  offer_generated: colors.blue[500],
  signed: colors.teal[500],
  active: colors.teal[600],
  late: colors.warning,
  defaulted: colors.danger,
};
```
