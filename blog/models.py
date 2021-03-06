import itertools

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.CharField(max_length=100, db_index=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               limit_choices_to={'parent': None})

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['parent__name', 'name']

    def __str__(self):
        if self.parent:
            return "%s (%s)" % (self.name, self.parent)
        else:
            return "%s" % self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category', kwargs=dict(slug=self.slug))

    def children(self):
        return Category.objects.filter(parent=self)

    def descendants(self):
        children = self.children().values('id', 'name', 'slug')
        if children:
            for c in children:
                childs_descendants = Category.objects.get(
                    id=c['id']).descendants()
                if childs_descendants:
                    c['children'] = childs_descendants
                else:
                    c['children'] = None
            return c
        else:
            return None

    @classmethod
    def tree(cls):
        roots = cls.objects.filter(parent=None)
        res = []
        for r in roots:
            res.append({
                'id': r.id,
                'name': r.name,
                'slug': r.slug,
                'children': r.children().values('id', 'name', 'slug')
            })
        return res


class Post(models.Model):
    STATUS_CHOICES = (
        ('p', 'Published'),
        ('d', 'Draft'),
        ('u', 'Unpublished')
    )
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, blank=True)
    body = models.TextField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES,
                              default='d')
    created = models.DateTimeField(db_index=True, blank=True)
    modified = models.DateTimeField(blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True,
                                 limit_choices_to={'category__parent': None})
    owner = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post', kwargs=dict(
            year=self.year(), month=self.month(), day=self.day(),
            slug=self.slug))

    def year(self):
        return "{0}".format(self.created.year)

    def month(self):
        return "{0:02d}".format(self.created.month)

    def day(self):
        return "{0:02d}".format(self.created.day)

    def publish(self):
        self.status = 'p'
        self.save()

    def unpublish(self):
        self.status = 'u'
        self.save()

    def is_published(self):
        return self.status == 'p'

    def tagged(self):
        return ", ".join([t['name'] for t in self.tags.values()])

    def related(self):
        tags = self.tags.all()
        return Post.objects.filter(status='p', tags__in=tags).exclude(
            id=self.id).distinct()

    @classmethod
    def archive_tree(cls):
        dates = Post.objects.filter(status='p').values('created')
        d_list = [d['created'].date() for d in dates]

        tree = []
        # Group by year
        tree = [{
            'year': year,
            'months': [{
                'month': g.month,
                'name': g.strftime('%B')
            } for g in group]
        } for year, group in itertools.groupby(d_list, key=lambda x: x.year)]

        # Group by month
        for y in tree:
            y['months'] = [{
                'month': month,
                'name': [g['name'] for g in group][0]
            } for month, group in itertools.groupby(
                y['months'],
                key=lambda x: x['month']
            )]
        return tree
