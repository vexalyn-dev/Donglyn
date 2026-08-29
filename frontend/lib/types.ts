// Donglyn TypeScript Types

export interface PosterImage {
  url: string;
  alt?: string;
}

export interface PosterCardData {
  id: string;
  title: string;
  url: string;
  poster: string;
  episode?: string;
  status?: 'Ongoing' | 'Completed' | 'Upcoming';
  rating?: number;
  year?: string;
  genres?: string[];
  badge?: string;
}

export interface BannerItem {
  id: string;
  title: string;
  url: string;
  poster: string;
  subtitle?: string;
  description?: string;
}

export interface SectionData {
  section_name: string;
  total_items: number;
  data: PosterCardData[];
  more_url?: string;
  archive_url?: string;
}

export interface HomeData {
  creator: string;
  statusCode: number;
  status: string;
  elapsed_time: string;
  fallback?: boolean;
  sections: SectionData[];
  banners: BannerItem[];
  schedule?: ScheduleItem[];
  genres?: GenreItem[];
}

export interface GenreItem {
  name: string;
  slug: string;
  count?: number;
}

export interface ScheduleItem {
  day: string;
  items: PosterCardData[];
}

export interface DetailData {
  title: string;
  poster: string;
  backdrop?: string;
  rating?: number;
  year?: string;
  status?: string;
  genres?: string[];
  description?: string;
  episodes?: EpisodeData[];
  servers?: string[];
}

export interface EpisodeData {
  episode: string;
  title?: string;
  url: string;
  date?: string;
}

export interface BookmarkItem {
  id: string;
  donghua_id: string;
  title: string;
  url: string;
  poster: string;
  created_at: string;
}

export interface HistoryItem {
  id: string;
  donghua_id: string;
  title: string;
  url: string;
  poster: string;
  episode?: string;
  progress?: number;
  last_watched: string;
}

export interface UserData {
  id?: number;
  email: string;
  username?: string;
  avatar?: string;
  is_verified?: boolean;
  created_at?: string;
  bio?: string;
}

export interface SearchResponse {
  query: string;
  results: PosterCardData[];
  total?: number;
}

export interface PlayerData {
  title: string;
  episode_label: string;
  episodes: EpisodeData[];
  iframe_url: string;
  iframe_proxy: boolean;
  servers: string[];
  clean_url: string;
  current_server: string;
  original_url: string;
}
