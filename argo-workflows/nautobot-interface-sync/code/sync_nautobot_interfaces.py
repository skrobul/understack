import sushy
from models import Chassis
from helpers import (
    setup_logger,
    arg_parser,
    credential,
    oob_sushy_session,
    exit_with_error,
    is_off_board,
)
from nautobot import Nautobot

logger = setup_logger(__name__)


def main():
    parser = arg_parser(__file__)
    args = parser.parse_args()

    default_nb_url = "http://nautobot-default.nautobot.svc.cluster.local"
    device_name = args.hostname
    nb_url = args.nautobot_url or default_nb_url
    nb_token = args.nautobot_token or credential("nb-token", "token")
    oob_username = args.oob_username or credential("oob-secrets", "username")
    oob_password = args.oob_password or credential("oob-secrets", "password")

    nautobot = Nautobot(nb_url, nb_token, logger=logger)
    oob_ip = nautobot.device_oob_ip(device_name)
    oob = oob_sushy_session(oob_ip, oob_username, oob_password)

    try:
        chassis = Chassis.from_redfish(oob)
    except sushy.exceptions.AccessError as e:
        exit_with_error(e)

    interfaces = [
        interface
        for interface in chassis.network_interfaces
        if is_off_board(interface)
    ]

    nautobot.bulk_create_interfaces(device_name, interfaces)


if __name__ == "__main__":
    main()
