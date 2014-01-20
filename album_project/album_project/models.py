import os
import random
import zipfile
from datetime import datetime
from inspect import isclass

from django.utils.timezone import now
from django.db import models
from django.db.models.signals import post_init
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
try:
    from django.utils.encoding import force_text
except ImportError:
    # Django < 1.4.2
    from django.utils.encoding import force_unicode as force_text
from django.utils.encoding import smart_str, filepath_to_uri
from django.utils.functional import curry
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

# Required PIL classes may or may not be available from the root namespace
# depending on the installation method used.
try:
    import Image
    import ImageFile
    import ImageFilter
    import ImageEnhance
except ImportError:
    try:
        from PIL import Image
        from PIL import ImageFile
        from PIL import ImageFilter
        from PIL import ImageEnhance
    except ImportError:
        raise ImportError(
            'Album was unable to import the Python Imaging Library. Please confirm it`s installed and available on your current Python path.')

# attempt to load the django-tagging TagField from default location,
# otherwise we substitude a dummy TagField.
try:
    from tagging.fields import TagField
    tagfield_help_text = _('Separate tags with spaces, put quotes around multiple-word tags.')
except ImportError:
    class TagField(models.CharField):

        def __init__(self, **kwargs):
            default_kwargs = {'max_length': 255, 'blank': True}
            default_kwargs.update(kwargs)
            super(TagField, self).__init__(**default_kwargs)

        def get_internal_type(self):
            return 'CharField'
    tagfield_help_text = _('Django-tagging was not found, tags will be treated as plain text.')

    # Tell South how to handle this custom field.
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^album_project\.models\.TagField"])

from .utils import EXIF
from .utils.reflection import add_reflection

# Default limit for gallery.latest
LATEST_LIMIT = getattr(settings, 'ALBUM_GALLERY_LATEST_LIMIT', None)

# Number of random images from the gallery to display.
SAMPLE_SIZE = getattr(settings, 'ALBUM_GALLERY_SAMPLE_SIZE', 5)

# max_length setting for the ImageModel ImageField
IMAGE_FIELD_MAX_LENGTH = getattr(settings, 'ALBUM_IMAGE_FIELD_MAX_LENGTH', 100)

# Path to sample image
SAMPLE_IMAGE_PATH = getattr(settings, 'ALBUM_SAMPLE_IMAGE_PATH', os.path.join(
    os.path.dirname(__file__), 'res', 'sample.jpg'))  # os.path.join(settings.PROJECT_PATH, 'photologue', 'res', 'sample.jpg'

# Modify image file buffer size.
ImageFile.MAXBLOCK = getattr(settings, 'ALBUM_MAXBLOCK', 256 * 2 ** 10)

# Photologue image path relative to media root
ALBUM_DIR = getattr(settings, 'ALBUM_DIR', 'album')

# Look for user function to define file paths
ALBUM_PATH = getattr(settings, 'ALBUM_PATH', None)
if ALBUM_PATH is not None:
    if callable(ALBUM_PATH):
        get_storage_path = ALBUM_PATH
    else:
        parts = ALBUM_PATH.split('.')
        module_name = '.'.join(parts[:-1])
        module = import_module(module_name)
        get_storage_path = getattr(module, parts[-1])
else:
    def get_storage_path(instance, filename):
        return os.path.join(ALBUM_DIR, 'photos', filename)

# Quality options for JPEG images
JPEG_QUALITY_CHOICES = (
    (30, _('Very Low')),
    (40, _('Low')),
    (50, _('Medium-Low')),
    (60, _('Medium')),
    (70, _('Medium-High')),
    (80, _('High')),
    (90, _('Very High')),
)

# choices for new crop_anchor field in Photo
CROP_ANCHOR_CHOICES = (
    ('top', _('Top')),
    ('right', _('Right')),
    ('bottom', _('Bottom')),
    ('left', _('Left')),
    ('center', _('Center (Default)')),
)

IMAGE_TRANSPOSE_CHOICES = (
    ('FLIP_LEFT_RIGHT', _('Flip left to right')),
    ('FLIP_TOP_BOTTOM', _('Flip top to bottom')),
    ('ROTATE_90', _('Rotate 90 degrees counter-clockwise')),
    ('ROTATE_270', _('Rotate 90 degrees clockwise')),
    ('ROTATE_180', _('Rotate 180 degrees')),
)


# Prepare a list of image filters
filter_names = []
for n in dir(ImageFilter):
    klass = getattr(ImageFilter, n)
    if isclass(klass) and issubclass(klass, ImageFilter.BuiltinFilter) and \
    hasattr(klass, 'name'):
        filter_names.append(klass.__name__)
IMAGE_FILTERS_HELP_TEXT = _(
    'Chain multiple filters using the following pattern "FILTER_ONE->FILTER_TWO->FILTER_THREE". Image filters will be applied in order. The following filters are available: %s.' % (', '.join(filter_names)))


class Gallery(models.Model):
    date_added = models.DateTimeField(_('date published'),
                                      default=now)
    title = models.CharField(_('title'),
                             max_length=50,
                             unique=True)
    title_slug = models.SlugField(_('title slug'),
                                  unique=True,
                                  help_text=_('A "slug" is a unique URL-friendly title for an object.'))
    description = models.TextField(_('description'),
                                   blank=True)
    is_public = models.BooleanField(_('is public'),
                                    default=True,
                                    help_text=_('Public galleries will be displayed '
                                    'in the default views.'))
    photos = models.ManyToManyField('Photo',
                                    related_name='galleries',
                                    verbose_name=_('photos'),
                                    null=True,
                                    blank=True)
    tags = TagField(help_text=tagfield_help_text, verbose_name=_('tags'))

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = _('gallery')
        verbose_name_plural = _('galleries')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('al-gallery', args=[self.title_slug])

    def latest(self, limit=LATEST_LIMIT, public=True):
        if not limit:
            limit = self.photo_count()
        if public:
            return self.public()[:limit]
        else:
            return self.photos.all()[:limit]

    def photo_count(self, public=True):
        """Return a count of all the photos in this gallery."""
        if public:
            return self.public().count()
        else:
            return self.photos.all().count()
    photo_count.short_description = _('count')

    def public(self):
        """Return a queryset of all the public photos in this gallery."""
        return self.photos.filter(is_public=True)


class GalleryUpload(models.Model):
    zip_file = models.FileField(_('images file (.zip)'),
                                upload_to=ALBUM_DIR + "/temp",
                                help_text=_('Select a .zip file of images to upload into a new Gallery.'))
    gallery = models.ForeignKey(Gallery,
                                verbose_name=_('gallery'),
                                null=True,
                                blank=True,
                                help_text=_('Select a gallery to add these images to. '
                                            'Leave this empty to create a new gallery from the '
                                            'supplied title.'))
    title = models.CharField(_('title'),
                             max_length=50,
                             help_text=_('All photos in the gallery will be given a '
                                         'title made up of the gallery title + a '
                                         'sequential number.'))
    caption = models.TextField(_('caption'),
                               blank=True,
                               help_text=_('Caption will be added to all photos.'))
    description = models.TextField(_('description'),
                                   blank=True,
                                   help_text=_('A description of this Gallery.'))
    is_public = models.BooleanField(_('is public'),
                                    default=True,
                                    help_text=_('Uncheck this to make the uploaded '
                                                'gallery and included photographs private.'))
    tags = models.CharField(max_length=255,
                            blank=True,
                            help_text=tagfield_help_text,
                            verbose_name=_('tags'))

    class Meta:
        verbose_name = _('gallery upload')
        verbose_name_plural = _('gallery uploads')

    def save(self, *args, **kwargs):
        super(GalleryUpload, self).save(*args, **kwargs)
        gallery = self.process_zipfile()
        super(GalleryUpload, self).delete()
        return gallery


class ImageModel(models.Model):
    image = models.ImageField(_('image'),
                              max_length=IMAGE_FIELD_MAX_LENGTH,
                              upload_to=get_storage_path)
    date_taken = models.DateTimeField(_('date taken'),
                                      null=True,
                                      blank=True,
                                      editable=False)
    view_count = models.PositiveIntegerField(_('view count'),
                                             default=0,
                                             editable=False)
    crop_from = models.CharField(_('crop from'),
                                 blank=True,
                                 max_length=10,
                                 default='center',
                                 choices=CROP_ANCHOR_CHOICES)

    class Meta:
        abstract = True

    @property
    def EXIF(self):
        try:
            return EXIF.process_file(open(self.image.path, 'rb'))
        except:
            try:
                return EXIF.process_file(open(self.image.path, 'rb'), details=False)
            except:
                return {}

    def admin_thumbnail(self):
        func = getattr(self, 'get_admin_thumbnail_url', None)
        if func is None:
            return _('An "admin_thumbnail" photo size has not been defined.')
        else:
            if hasattr(self, 'get_absolute_url'):
                return u'<a href="%s"><img src="%s"></a>' % \
                    (self.get_absolute_url(), func())
            else:
                return u'<a href="%s"><img src="%s"></a>' % \
                    (self.image.url, func())
    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True

    def cache_path(self):
        return os.path.join(os.path.dirname(self.image.path), "cache")

    def cache_url(self):
        return '/'.join([os.path.dirname(self.image.url), "cache"])

    def image_filename(self):
        return os.path.basename(force_text(self.image.path))


    #add for getting upload file name as the tile and title_slug
    def image_name(self):
        name=os.path.basename(force_text(self.image.path))
        name.split('.')
        return name.split('.')[0]

    def _get_filename_for_size(self, size):
        size = getattr(size, 'name', size)
        base, ext = os.path.splitext(self.image_filename())
        return ''.join([base, '_', size, ext])

    def _get_SIZE_photosize(self, size):
        return PhotoSizeCache().sizes.get(size)

    def _get_SIZE_size(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        if not self.size_exists(photosize):
            self.create_size(photosize)
        return Image.open(self._get_SIZE_filename(size)).size

    def _get_SIZE_url(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        if not self.size_exists(photosize):
            self.create_size(photosize)
        if photosize.increment_count:
            self.increment_count()
        return '/'.join([
            self.cache_url(),
            filepath_to_uri(self._get_filename_for_size(photosize.name))])

    def _get_SIZE_filename(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        return smart_str(os.path.join(self.cache_path(),
                                      self._get_filename_for_size(photosize.name)))

    def increment_count(self):
        self.view_count += 1
        models.Model.save(self)

    def add_accessor_methods(self, *args, **kwargs):
        for size in PhotoSizeCache().sizes.keys():
            setattr(self, 'get_%s_size' % size,
                    curry(self._get_SIZE_size, size=size))
            setattr(self, 'get_%s_photosize' % size,
                    curry(self._get_SIZE_photosize, size=size))
            setattr(self, 'get_%s_url' % size,
                    curry(self._get_SIZE_url, size=size))
            setattr(self, 'get_%s_filename' % size,
                    curry(self._get_SIZE_filename, size=size))

    def size_exists(self, photosize):
        func = getattr(self, "get_%s_filename" % photosize.name, None)
        if func is not None:
            if os.path.isfile(func()):
                return True
        return False

    def resize_image(self, im, photosize):
        cur_width, cur_height = im.size
        new_width, new_height = photosize.size
        if photosize.crop:
            ratio = max(float(new_width) / cur_width, float(new_height) / cur_height)
            x = (cur_width * ratio)
            y = (cur_height * ratio)
            xd = abs(new_width - x)
            yd = abs(new_height - y)
            x_diff = int(xd / 2)
            y_diff = int(yd / 2)
            if self.crop_from == 'top':
                box = (int(x_diff), 0, int(x_diff + new_width), new_height)
            elif self.crop_from == 'left':
                box = (0, int(y_diff), new_width, int(y_diff + new_height))
            elif self.crop_from == 'bottom':
                box = (int(x_diff), int(yd), int(x_diff + new_width), int(y))  # y - yd = new_height
            elif self.crop_from == 'right':
                box = (int(xd), int(y_diff), int(x), int(y_diff + new_height))  # x - xd = new_width
            else:
                box = (int(x_diff), int(y_diff), int(x_diff + new_width), int(y_diff + new_height))
            im = im.resize((int(x), int(y)), Image.ANTIALIAS).crop(box)
        else:
            if not new_width == 0 and not new_height == 0:
                ratio = min(float(new_width) / cur_width,
                            float(new_height) / cur_height)
            else:
                if new_width == 0:
                    ratio = float(new_height) / cur_height
                else:
                    ratio = float(new_width) / cur_width
            new_dimensions = (int(round(cur_width * ratio)),
                              int(round(cur_height * ratio)))
            if new_dimensions[0] > cur_width or \
               new_dimensions[1] > cur_height:
                if not photosize.upscale:
                    return im
            im = im.resize(new_dimensions, Image.ANTIALIAS)
        return im

    def create_size(self, photosize):
        if self.size_exists(photosize):
            return
        if not os.path.isdir(self.cache_path()):
            os.makedirs(self.cache_path())
        try:
            im = Image.open(self.image.path)
        except IOError:
            return
        # Save the original format
        im_format = im.format
        # Resize/crop image
        if im.size != photosize.size and photosize.size != (0, 0):
            im = self.resize_image(im, photosize)
        # Save file
        im_filename = getattr(self, "get_%s_filename" % photosize.name)()
        try:
            if im_format != 'JPEG':
                try:
                    im.save(im_filename)
                    return
                except KeyError:
                    pass
            im.save(im_filename, 'JPEG', quality=int(photosize.quality), optimize=True)
        except IOError as e:
            if os.path.isfile(im_filename):
                os.unlink(im_filename)
            raise e

    def remove_size(self, photosize, remove_dirs=True):
        if not self.size_exists(photosize):
            return
        filename = getattr(self, "get_%s_filename" % photosize.name)()
        if os.path.isfile(filename):
            os.remove(filename)
        if remove_dirs:
            self.remove_cache_dirs()

    def clear_cache(self):
        cache = PhotoSizeCache()
        for photosize in cache.sizes.values():
            self.remove_size(photosize, False)
        self.remove_cache_dirs()

    def pre_cache(self):
        cache = PhotoSizeCache()
        for photosize in cache.sizes.values():
            if photosize.pre_cache:
                self.create_size(photosize)

    def remove_cache_dirs(self):
        try:
            os.removedirs(self.cache_path())
        except:
            pass

    def save(self, *args, **kwargs):
        if self.date_taken is None:
            try:
                exif_date = self.EXIF.get('EXIF DateTimeOriginal', None)
                if exif_date is not None:
                    d, t = str.split(exif_date.values)
                    year, month, day = d.split(':')
                    hour, minute, second = t.split(':')
                    self.date_taken = datetime(int(year), int(month), int(day),
                                               int(hour), int(minute), int(second))
            except:
                pass
        if self.date_taken is None:
            self.date_taken = now()
        if self._get_pk_val():
            self.clear_cache()
        super(ImageModel, self).save(*args, **kwargs)
        self.pre_cache()

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (
            self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        # Files associated to a FileField have to be manually deleted:
        # https://docs.djangoproject.com/en/dev/releases/1.3/#deleting-a-model-doesn-t-delete-associated-files
        # http://haineault.com/blog/147/
        # The data loss scenarios mentioned in the docs hopefully do not apply
        # to Photologue!
        path = self.image.path
        super(ImageModel, self).delete()
        os.remove(path)


class Photo(ImageModel):
    title = models.CharField(_('title'),
                             max_length=50,
                             unique=True)
    title_slug = models.SlugField(_('slug'),
                                  unique=True,
                                  help_text=_('A "slug" is a unique URL-friendly title for an object.'))
    caption = models.TextField(_('caption'),
                               blank=True)
    date_added = models.DateTimeField(_('date added'),
                                      default=now)
    is_public = models.BooleanField(_('is public'),
                                    default=True,
                                    help_text=_('Public photographs will be displayed in the default views.'))
    tags = TagField(help_text=tagfield_help_text, verbose_name=_('tags'))

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = _("photo")
        verbose_name_plural = _("photos")

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.title_slug is None:
            self.title_slug = slugify(self.title)
        super(Photo, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('al-photo', args=[self.title_slug])

    def public_galleries(self):
        """Return the public galleries to which this photo belongs."""
        return self.galleries.filter(is_public=True)

    def get_previous_in_gallery(self, gallery):
        try:
            return self.get_previous_by_date_added(galleries__exact=gallery,
                                                   is_public=True)
        except Photo.DoesNotExist:
            return None

    def get_next_in_gallery(self, gallery):
        try:
            return self.get_next_by_date_added(galleries__exact=gallery,
                                               is_public=True)
        except Photo.DoesNotExist:
            return None



class PhotoSize(models.Model):
    name = models.CharField(_('name'),
                            max_length=40,
                            unique=True,
                            help_text=_('Photo size name should contain only letters, numbers and underscores. Examples: "thumbnail", "display", "small", "main_page_widget".'))
    width = models.PositiveIntegerField(_('width'),
                                        default=0,
                                        help_text=_('If width is set to "0" the image will be scaled to the supplied height.'))
    height = models.PositiveIntegerField(_('height'),
                                         default=0,
                                         help_text=_('If height is set to "0" the image will be scaled to the supplied width'))
    quality = models.PositiveIntegerField(_('quality'),
                                          choices=JPEG_QUALITY_CHOICES,
                                          default=70,
                                          help_text=_('JPEG image quality.'))
    upscale = models.BooleanField(_('upscale images?'),
                                  default=False,
                                  help_text=_('If selected the image will be scaled up if necessary to fit the supplied dimensions. Cropped sizes will be upscaled regardless of this setting.'))
    crop = models.BooleanField(_('crop to fit?'),
                               default=False,
                               help_text=_('If selected the image will be scaled and cropped to fit the supplied dimensions.'))
    pre_cache = models.BooleanField(_('pre-cache?'),
                                    default=False,
                                    help_text=_('If selected this photo size will be pre-cached as photos are added.'))
    increment_count = models.BooleanField(_('increment view count?'),
                                          default=False,
                                          help_text=_('If selected the image\'s "view_count" will be incremented when this photo size is displayed.'))
    class Meta:
        ordering = ['width', 'height']
        verbose_name = _('photo size')
        verbose_name_plural = _('photo sizes')

    def __unicode__(self):
        return self.name

    def clear_cache(self):
        for cls in ImageModel.__subclasses__():
            for obj in cls.objects.all():
                obj.remove_size(self)
                if self.pre_cache:
                    obj.create_size(self)
        PhotoSizeCache().reset()

    def clean(self):
        if self.crop is True:
            if self.width == 0 or self.height == 0:
                raise ValidationError(_("Can only crop photos if both width and height dimensions are set."))

    def save(self, *args, **kwargs):
        super(PhotoSize, self).save(*args, **kwargs)
        PhotoSizeCache().reset()
        self.clear_cache()

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (
            self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        super(PhotoSize, self).delete()

    def _get_size(self):
        return (self.width, self.height)

    def _set_size(self, value):
        self.width, self.height = value
    size = property(_get_size, _set_size)


class PhotoSizeCache(object):
    __state = {"sizes": {}}

    def __init__(self):
        self.__dict__ = self.__state
        if not len(self.sizes):
            sizes = PhotoSize.objects.all()
            for size in sizes:
                self.sizes[size.name] = size

    def reset(self):
        self.sizes = {}


# Set up the accessor methods
def add_methods(sender, instance, signal, *args, **kwargs):
    """ Adds methods to access sized images (urls, paths)

    after the Photo model's __init__ function completes,
    this method calls "add_accessor_methods" on each instance.
    """
    if hasattr(instance, 'add_accessor_methods'):
        instance.add_accessor_methods()

# connect the add_accessor_methods function to the post_init signal
post_init.connect(add_methods)
