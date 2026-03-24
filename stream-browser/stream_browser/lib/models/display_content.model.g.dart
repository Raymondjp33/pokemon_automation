// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'display_content.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

DisplayContent _$DisplayContentFromJson(Map<String, dynamic> json) =>
    DisplayContent(
      game: json['game'] as String,
      huntType: json['huntType'] as String,
      oddsString: json['oddsString'] as String?,
      huntId: json['hunt_id'] as num?,
    );

Map<String, dynamic> _$DisplayContentToJson(DisplayContent instance) =>
    <String, dynamic>{
      'game': instance.game,
      'huntType': instance.huntType,
      'oddsString': instance.oddsString,
      'hunt_id': instance.huntId,
    };
