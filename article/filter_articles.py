from user.models import User, Profile
def filter_article(payload,published_from,published_to,author_user):
    if published_from is not None or published_to is not None or author_user is not None:
        if published_from is None and published_to is not None:
            published_to_date = datetime.strptime(published_to, '%Y-%m-%d')
            payload['published_on__lte'] = published_to_date
        if published_from is not None and published_to is not None:
            published_from_date = datetime.strptime(published_from, '%Y-%m-%d')
            published_to_date = datetime.strptime(published_to, '%Y-%m-%d')
            payload['published_on__range'] = (published_from_date, published_to_date)
        if author_user is not None:
            profile = Profile.objects.filter(user_id_profile=author_user).first()
            payload['author_user'] = profile.user
        payload.pop('published_from', None)
        payload.pop('published_to', None)
        return payload
