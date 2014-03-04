from app import db, models
from flask import session, redirect, url_for, request, flash
from flask.ext.admin import Admin, AdminIndexView, expose
from flask.ext.admin.base import MenuLink
from flask.ext.admin.contrib.sqla import ModelView
from utils import make_slug

from flask.ext.admin.babel import gettext
from flask.ext.admin.helpers import validate_form_on_submit
from flask.ext.admin.model.helpers import get_mdict_item_or_list


class AuthMixin(object):
    def is_accessible(self):
        return 'logged_in' in session

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login'))


class MyAdminIndexView(AuthMixin, AdminIndexView):
    pass


class AdminModelView(AuthMixin, ModelView):
    pass


class CategoryView(AdminModelView):
    form_excluded_columns = ['community_reviews', ]


class RoleView(AdminModelView):
    form_excluded_columns = ['users', ]


class UserView(AdminModelView):
    form_excluded_columns = ['community_reviews', 'user_reviews', ]


class GroupView(AdminModelView):
    form_excluded_columns = ['community_reviews', ]


class CommunityReviewView(AdminModelView):
    form_excluded_columns = ['user_reviews', 'slug', 'reddit_score', 'last_crawl', ]
    list_template = 'admin/community_review_list.html'

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = url_for('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()

        if validate_form_on_submit(form):

            new_slug = make_slug(form.title.data)
            slug_check = None
            slug_check = db.session.query(models.CommunityReview)\
                .filter_by(category_id=form.category.data.id)\
                .filter_by(slug=new_slug).first()

            if not slug_check:
                if self.create_model(form):
                    if '_add_another' in request.form:
                        flash(gettext('Model was successfully created.'))
                        return redirect(url_for(
                            '.create_view',
                            url=return_url)
                        )
                    else:
                        return redirect(return_url)
            else:
                flash('Title must be unique to the category')

        form_opts = None

        return self.render(self.create_template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = url_for('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            return redirect(return_url)

        form = self.edit_form(obj=model)
        new_slug = make_slug(form.title.data)
        slug_check = None

        if new_slug != model.slug:
            slug_check = db.session.query(models.CommunityReview)\
                .filter_by(category_id=form.category.data.id)\
                .filter_by(slug=new_slug).first()

        if validate_form_on_submit(form) and not slug_check:
            if new_slug != model.slug:
                model.slug = new_slug
            if self.update_model(form, model):
                if '_continue_editing' in request.form:
                    flash(gettext('Model was successfully saved.'))
                    return redirect(request.url)
                else:
                    return redirect(return_url)
        elif slug_check:
            flash(gettext('Title must be unique to the category'))

        form_opts = None

        return self.render(self.edit_template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)

# Admin construtor
admin = Admin(
    name="RedditReviewBot",
    index_view=MyAdminIndexView(),
    base_template="admin/my_base.html"
)

# add admin views
admin.add_view(CategoryView(
    models.Category,
    db.session,
    name='Categories',
    endpoint='category_model_view'
))
admin.add_view(RoleView(
    models.Role,
    db.session,
    name='Roles',
    endpoint='role_model_view'
))
admin.add_view(UserView(
    models.User,
    db.session,
    name='Users',
    endpoint='user_model_view'
))
admin.add_view(GroupView(models.Group, db.session))
admin.add_view(CommunityReviewView(
    models.CommunityReview,
    db.session,
    name='Community Reviews',
    endpoint='communityreview_model_view'
))
admin.add_view(AdminModelView(
    models.UserReview,
    db.session,
    name='User Reviews',
    endpoint='userreview_model_view'
))

logout_link = MenuLink(name='Logout', url='/logout')
admin.add_link(logout_link)
