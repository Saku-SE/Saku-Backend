from django.db.models import Sum, Count
from auction.models import Auction
from bid.models import Bid

# - daramad
def get_income(user, all_auctions):
    income = all_auctions.filter(user=user, best_bid__isnull=False).aggregate(
        Sum("best_bid__price")
    )["best_bid__price__sum"]
    return 0 if income == None else income


# - tedad auction movafagh (best_bid.user=user and finished_at > datetime.now)
def get_seccussfull_auction_count(user, all_auctions):
    return all_auctions.filter(best_bid__user=user).count()


# - participant num on my auctions
def get_auctions_participants_num(all_user_auctions):
    return all_user_auctions.aggregate(Sum("participants_num"))["participants_num__sum"]


# - tedad my auctions
def get_auctions_count(all_user_auctions):
    return all_user_auctions.count()


# - 5 ta az akharin mozayede sherkat karde :
#   - mode
#   - name
#   - started_at
#   - finished_at
#   - vaziat (barande, bazande)
def get_last_auctions_participated(user, all_user_bids):
    all_user_bids = all_user_bids.order_by("-time")
    last_auctions = []
    auctions = set()
    SUCCESSFULL_STATE = "successfull"
    FAILED_STATE = "failed"
    UNKNOWN_STATE = "unknown"
    for user_bid in all_user_bids:
        if len(auctions) == 5:
            break
        if user_bid.auction.pk not in auctions:
            auction: Auction = user_bid.auction
            auctions.add(auction.pk)
            best_bid: Bid = auction.best_bid
            if best_bid is None:
                success = UNKNOWN_STATE
            else:
                success = SUCCESSFULL_STATE if best_bid.user == user else FAILED_STATE
            auction_info = auction.__dict__
            auction_info = {
                'mode': auction_info['mode'],
                'name': auction_info['name'],
                'created_at': auction_info['created_at'],
                'finished_at': auction_info['finished_at'],
                'success': success,
            }
            last_auctions.append(auction_info)
    return last_auctions


# - 5 ta az akharin mozayede ijad karde :
#   - mode
#   - name
#   - participant num
#   - started_at
#   - finished_at
#   - best_bid
#   - cathegory
def get_last_auctions_created(all_user_auctions):
    return all_user_auctions.order_by("-created_at").values(
        "mode",
        "name",
        "participants_num",
        "created_at",
        "finished_at",
        "best_bid",
        "category",
    )[:5]


# - list daramad ha
def get_income_list(user, all_auctions):
    auctions = all_auctions.filter(user=user, best_bid__isnull=False)
    income_list = [auction.best_bid.price for auction in auctions]
    return income_list


# - mizane mosharekate shoma
def get_your_colaberation_list(all_user_bids, all_user_auctions):
    colaberation_count = (
        all_user_auctions.values("created_at__date")
        .annotate(count=Count("id"))
        .order_by("created_at__date")
        .union(
            all_user_bids.values_list("time__date")
            .annotate(count=Count("id"))
            .order_by("time__date")
        )
    )
    ### TODO:
    ### does union work?
    colaberation_list = [colaberation["count"] for colaberation in colaberation_count]
    return colaberation_list


def get_your_colaberation_count(all_user_bids, all_user_auctions):
    return all_user_auctions.count() + all_user_bids.count()


# - list moshahede afrad az my auction
def get_others_colaberation_list(user, all_bids):
    colaberation_count = (
        all_bids.filter(auction__user=user)
        .values("time__date")
        .annotate(count=Count("id"))
        .order_by("time__date")
    )
    colaberation_list = [colaberation["count"] for colaberation in colaberation_count]
    return colaberation_list


def get_others_colaberation_count(user, all_bids):
    return all_bids.filter(auction__user=user).count()


# - list hazine ha
def get_expense_list(all_user_bids, all_auctions):
    expense_list = []
    for user_bid in all_user_bids:
        if all_auctions.filter(best_bid=user_bid).exists():
            expense_list.append(user_bid.price)
    return expense_list


def get_expense(all_user_bids, all_auctions):
    expense = 0
    for user_bid in all_user_bids:
        if all_auctions.filter(best_bid=user_bid).exists():
            expense += user_bid.price
    return expense


def get_auction_participate_count(user, all_bids, auction_mode):
    auction_participate = set()
    all_user_bids = all_bids.filter(user=user, auction__mode=auction_mode)
    for user_bid in all_user_bids:
        auction_participate.add(user_bid.auction)
    return len(auction_participate)

def get_auction_create_count(user, all_auctions, auction_mode):
    return all_auctions.filter(user=user, mode=auction_mode).count()

# - tedad auction mode 1 sherkat karde
def get_auction1_participate_count(user, all_bids):
    return get_auction_participate_count(user, all_bids, 1)


# - tedad auction mode 1 ijad karde
def get_auction1_create_count(user, all_auctions):
    return get_auction_create_count(user, all_auctions, 1)


# - tedad auction mode 2 sherkat karde
def get_auction2_participate_count(user, all_bids):
    return get_auction_participate_count(user, all_bids, 2)


# - tedad auction mode 2 ijad karde
def get_auction2_create_count(user, all_auctions):
    return get_auction_create_count(user, all_auctions, 2)


# - payam haye akhir
def get_last_chats(user):
    # username = user.username
    pass


# - list az:
#   - hazine, daramad -> entekhabe sal
def get_yearly_income_list(user, year, all_auctions):
    auctions = all_auctions.filter(
        user=user, finished_at__year=year, best_bid__isnull=False
    )
    income_list = [auction.best_bid.price for auction in auctions]
    return income_list


def get_yearly_expense_list(year, all_user_bids, all_auctions):
    expense_list = []
    for user_bid in all_user_bids:
        if all_auctions.filter(best_bid=user_bid, finished_at__year=year).exists():
            expense_list.append(user_bid.price)
    return expense_list
