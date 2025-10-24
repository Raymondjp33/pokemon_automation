import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'pages/control_panel/control_panel_state.dart';
import 'pages/one_switch/one_switch_state.dart';
import 'pages/stats/stats_state.dart';
import 'pages/three_switch/three_switch_state.dart';

class NavKeyService {
  static GlobalKey<NavigatorState> globalNavigationKey =
      GlobalKey<NavigatorState>();
}

enum ERoute {
  controlPanel(name: 'controlPanel', path: '/'),
  threeSwitch(name: 'threeSwitch', path: '/threeSwitch'),
  oneSwitch(name: 'oneSwitch', path: '/oneSwitch'),
  stats(name: 'stats', path: '/stats');

  final String name;
  final String path;
  const ERoute({required this.name, required this.path});
}

final GoRouter router = GoRouter(
  navigatorKey: NavKeyService.globalNavigationKey,
  initialLocation: ERoute.stats.path,
  restorationScopeId: 'router',
  routes: <RouteBase>[
    GoRoute(
      name: ERoute.controlPanel.name,
      path: ERoute.controlPanel.path,
      builder: (BuildContext context, GoRouterState state) {
        return ControlPanel();
      },
    ),
    GoRoute(
      name: ERoute.stats.name,
      path: ERoute.stats.path,
      builder: (BuildContext context, GoRouterState state) {
        return Stats();
      },
    ),
    GoRoute(
      name: ERoute.threeSwitch.name,
      path: ERoute.threeSwitch.path,
      builder: (BuildContext context, GoRouterState state) {
        return ThreeSwitch();
      },
    ),
    GoRoute(
      name: ERoute.oneSwitch.name,
      path: ERoute.oneSwitch.path,
      builder: (BuildContext context, GoRouterState state) {
        return OneSwitch();
      },
    ),
  ],
);
