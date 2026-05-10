import { Image } from 'expo-image'
import { type ImageStyle, type StyleProp } from 'react-native'

type BrandMarkProps = {
  variant: 'logo' | 'mark'
  style?: StyleProp<ImageStyle>
}

const SOURCES = {
  logo: require('@/assets/images/lease-ai-wordmark.png'),
  mark: require('@/assets/images/lease-ai-mark.png'),
} as const

export function BrandMark({ variant, style }: BrandMarkProps) {
  return <Image source={SOURCES[variant]} contentFit="contain" style={style} />
}
