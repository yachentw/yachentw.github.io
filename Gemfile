# frozen_string_literal: true
source "https://rubygems.org"

# ----- site deps -----
gem "jekyll", "~> 4.4"
gem "beautiful-jekyll-theme", "~> 6.0"
gem "jekyll-paginate"
gem "jekyll-sitemap"

# Ruby 3+ sometimes needs this for local/dev; harmless on Linux
gem "webrick", "~> 1.9"

# ----- Windows / JRuby -----
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.1", :platforms => [:mingw, :x64_mingw, :mswin]
