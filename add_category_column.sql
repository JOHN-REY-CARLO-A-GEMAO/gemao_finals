-- Add category column to blog_posts table
ALTER TABLE blog_posts 
ADD COLUMN category ENUM('General', 'Updates', 'Announcements') DEFAULT 'General' AFTER tags;

-- Update existing posts to have 'General' as default category
UPDATE blog_posts SET category = 'General' WHERE category IS NULL;

-- Add index for category filtering
ALTER TABLE blog_posts ADD INDEX idx_category (category);
